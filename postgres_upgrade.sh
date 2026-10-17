#!/bin/bash

# Configuration
# -----------------------------------------------------------------------------

ENV_FILE=".env"
DATA_DIR="./db_data"
TARGET_IMAGE="postgres:18-alpine"
TARGET_VER="18"


# Do not modify anything below this line
# -----------------------------------------------------------------------------

# Pretty colors ;)
INFO="\033[34m>\033[0m"
OK="\033[32mSuccess\033[0m"
ERROR="\033[31mError\033[0m"

# Globals used by cleanup trap
SPINNER_BG_PID=""
MIGRATION_LOG=""


# Functions
# -----------------------------------------------------------------------------

# Cleanup handler
cleanup() {
    if [ -n "$SPINNER_BG_PID" ] && kill -0 "$SPINNER_BG_PID" 2>/dev/null; then
        kill "$SPINNER_BG_PID" 2>/dev/null
        wait "$SPINNER_BG_PID" 2>/dev/null
        printf "\r%-80s\r" " "
    fi
    rm -f "$MIGRATION_LOG" 2>/dev/null
}
trap cleanup EXIT INT TERM

# Usage  : run_with_spinner "message" <tmpfile> command [args...]
run_with_spinner() {
    local MSG="$1"
    local OUTFILE="$2"
    shift 2
    local SPINNER_FRAMES=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
    local START=$SECONDS
    local IDX=0

    "$@" > /dev/null 2>"$OUTFILE" &
    local CMD_PID=$!
    SPINNER_BG_PID=$CMD_PID

    while kill -0 "$CMD_PID" 2>/dev/null; do
        local LINE="$MSG  ${SPINNER_FRAMES[$IDX]}  $((SECONDS - START))s elapsed"
        printf "\r%s" "$LINE"
        IDX=$(( (IDX + 1) % 10 ))
        sleep 0.1
    done

    wait "$CMD_PID"
    local EXIT_CODE=$?
    SPINNER_BG_PID=""

    local LAST="$INFO $MSG  ${SPINNER_FRAMES[0]}  $((SECONDS - START))s elapsed"
    printf "\r%-${#LAST}s\r" " "

    return $EXIT_CODE
}

# User must be either 'root' or in the sudoers group
check_privileges() {
    if [ "$EUID" -eq 0 ]; then
        return 0
    fi

    printf "You're not 'root' : checking your 'sudo' privileges... "
    if ! sudo -n true 2>/dev/null; then
        printf "$ERROR\n"
        printf "  └ Please run as 'root' or ensure your user is in the sudoers file with NOPASSWD.\n"
        exit 1
    else
        printf "$OK\n"
        return 0
    fi
}

# get .env parameters values
get_env_var() {
    grep "^$1=" "$ENV_FILE" | cut -d'=' -f2- | sed 's/^"//;s/"$//;s/[[:space:]]*#.*$//'
}

# Start the postgres Docker container
# First argument : 0 / 1 (don't exit / exit... the whole script on failure)
# Second argument : exit value on failure
# Usage : start_postgres 1 1
start_postgres() {
    local COUNTER=0

    printf "$INFO Start postgres container...\n"

    if ! docker compose up -d postgres; then
        printf "└ $ERROR Docker failed to initiate postgres container.\n"
        printf "  └ Check you 'compose.yaml' file (?)\n"
        echo ""
        [ "$1" -eq 1 ] && exit "$2"
        return 1
    fi

    until docker compose exec -T \
            -e PGUSER="$DB_USER" \
            -e PGDATABASE="$DB_NAME" \
            postgres pg_isready > /dev/null 2>&1; do
        if [ "$COUNTER" -ge 60 ]; then
            printf "\n└ $ERROR postgres failed to start within 60s.\n"
            echo ""
            [ "$1" -eq 1 ] && exit "$2"
            return 1
        fi

        echo -n "."
        sleep 1
        ((COUNTER++))
    done

    echo " Ready!"
    printf "└ $OK\n"
    echo ""
    return 0
}

# Start (all in compose) Docker containers
start_containers() {
    printf "$INFO Starting all CRCON Docker containers...\n"

    if ! docker compose up -d --remove-orphans; then
        printf "└ $ERROR\n"
        echo ""
        [ "$1" -eq 1 ] && exit "$2"
        return 1
    else
        printf "└ $OK\n"
        echo ""
        return 0
    fi
}

# Stop (all in compose) Docker containers
stop_containers() {
    printf "$INFO Stopping all CRCON Docker containers...\n"

    if ! docker compose down; then
        printf "└ $ERROR\n"
        echo ""
        [ "$1" -eq 1 ] && exit "$2"
        return 1
    else
        printf "└ $OK\n"
        echo ""
        return 0
    fi
}

# Rollback
rollback() {
    printf "────────────────────────────────────────────────────────\n"
    printf "$INFO Start rollback procedure...\n"
    printf "────────────────────────────────────────────────────────\n"

    # Stop CRCON
    stop_containers 0 0

    # Restore .env
    printf "$INFO Restore '$ENV_FILE'\n"
    printf "────────────────────────────────────────────────────────\n"

    printf "$INFO Search for '$BACKUP_ENV'... "
    if [ -f "$BACKUP_ENV" ]; then
        printf "$OK\n"

        printf "$INFO Search for '$ENV_FILE'... "
        if [ -f $ENV_FILE ]; then
            printf "$OK\n"

            printf "└ $INFO Delete '$ENV_FILE' file... "
            sudo rm -f "$ENV_FILE" && printf "$OK\n" || printf "$ERROR\n"

        else
            printf "$ERROR\n"
        fi

        printf "└ $INFO Copy backup '$BACKUP_ENV' file to '$ENV_FILE'... "
        sudo cp "$BACKUP_ENV" "$ENV_FILE" && printf "$OK\n" || printf "$ERROR\n"

    else
        printf "$ERROR\n"
        printf "  └ $INFO You still can manually revert 'POSTGRES_IMAGE' to '$ORIGINAL_IMAGE' in '$ENV_FILE'.\n"
    fi

    # Restore ./db_data/
    printf "\n$INFO Restore '$DATA_DIR'\n"
    printf "────────────────────────────────────────────────────────\n"

    printf "$INFO Search for '$BACKUP_DIR'... "
    if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
        printf "$OK\n"

        printf "$INFO Search for '$DATA_DIR' folder... "
        if [ -d "$DATA_DIR" ]; then
            printf "$OK\n"

            printf "└ $INFO Delete '$DATA_DIR' folder... "
            sudo rm -rf "$DATA_DIR" && printf "$OK\n" || printf "$ERROR\n"

        else
            printf "$ERROR\n"
        fi

        printf "  └ $INFO Copy backup '$BACKUP_DIR' folder to '$DATA_DIR'... "
        sudo cp -rp "$BACKUP_DIR" "$DATA_DIR" && printf "$OK\n" || printf "$ERROR\n"

    else
        printf "$ERROR\n"
    fi
    echo ""

    # Restart CRCON
    start_containers 0

    # Report
    if [[ -f "$BACKUP_ENV" || ( -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ) ]]; then
        printf "────────────────────────────────────────────────────────\n"
        echo "[IMPORTANT]"
        if [ -f "$BACKUP_ENV" ]; then
            echo "- Your original $ENV_FILE file backup is: $BACKUP_ENV"
        fi
        if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
            echo "- Your original database backup is in: $BACKUP_DIR"
        fi
        echo "Make sure everything works as intended before deleting any backup."
        printf "────────────────────────────────────────────────────────\n"
    fi
}


# Script start
# -----------------------------------------------------------------------------

printf "────────────────────────────────────────────────────────\n"
echo "Starting postgres migration"
printf "────────────────────────────────────────────────────────\n"

check_privileges

printf "\n$INFO Get current postgres data version\n"
printf "────────────────────────────────────────────────────────\n"

printf "$INFO Search for '$DATA_DIR' folder... "
if [ ! -d "$DATA_DIR" ]; then
    printf "$ERROR\n"
    printf "└ $INFO Make sure you're running this script in CRCON root folder.\n"
    exit 1
fi
printf "$OK\n"

printf "└ $INFO Reading postgres version from '$DATA_DIR/PG_VERSION' file... "
CURRENT_VER=$(sudo cat "$DATA_DIR/PG_VERSION" 2>/dev/null)

if [ -z "$CURRENT_VER" ]; then
    printf " $ERROR\n"
    printf "  └ '$DATA_DIR/PG_VERSION' not found or not accessible.\n"
    exit 1
fi

if ! [[ "$CURRENT_VER" =~ ^[0-9]+$ ]]; then
    printf "$ERROR\n"
    printf "  └ '$DATA_DIR/PG_VERSION' contains non-digit characters.\n"
    exit 1
fi

printf "$OK\n"
printf "  └ $INFO Current version found: $CURRENT_VER\n"

if [ "$CURRENT_VER" == "$TARGET_VER" ]; then
    printf "    └ $INFO No migration needed.\n"
    exit 0
fi

printf "    └ $INFO Migration needed: from v$CURRENT_VER (current) to v$TARGET_VER (target).\n"


printf "\n$INFO Get current postgres parameters\n"
printf "────────────────────────────────────────────────────────\n"

printf "$INFO Search for '$ENV_FILE' file... "
if [ ! -f "$ENV_FILE" ]; then
    printf "$ERROR\n"
    printf "└ $INFO Make sure you're running this script in CRCON root folder.\n"
    exit 1
fi
printf "$OK\n"

printf "└ $INFO Checking parameters values...\n"
ORIGINAL_IMAGE=$(get_env_var "POSTGRES_IMAGE")
DB_USER=$(get_env_var "HLL_DB_USER")
DB_NAME=$(get_env_var "HLL_DB_NAME")
DB_PASS=$(get_env_var "HLL_DB_PASSWORD")

# Validate ORIGINAL_IMAGE (allows letters, digits, /, :, ., -, @)
if [ -z "$ORIGINAL_IMAGE" ]; then
    printf "  └ $ERROR ORIGINAL_IMAGE is empty.\n"
    exit 1
fi
if ! [[ "$ORIGINAL_IMAGE" =~ ^[a-zA-Z0-9_/.:@-]+$ ]]; then
    printf "  └ $ERROR ORIGINAL_IMAGE contains invalid characters.\n"
    exit 1
fi
printf "  └ $INFO ORIGINAL_IMAGE = $ORIGINAL_IMAGE\n"

# Validate DB_USER and DB_NAME (strict: letters, digits, _, -)
for var_name in "DB_USER" "DB_NAME"; do
    val=${!var_name}
    if [ -z "$val" ]; then
        printf "  └ $ERROR $var_name is empty.\n"
        exit 1
    fi
    if ! [[ "$val" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        printf "  └ $ERROR $var_name contains invalid characters (allowed: a-z, A-Z, 0-9, _, -).\n"
        exit 1
    fi
    printf "  └ $INFO $var_name = $val\n"
done

# Validate DB_PASS
if [ -z "$DB_PASS" ]; then
    printf "  └ $ERROR DB_PASS is empty.\n"
    exit 1
fi
if [[ "$DB_PASS" =~ [[:space:]] ]]; then
    printf "  └ $ERROR DB_PASS contains spaces.\n"
    exit 1
fi
printf "  └ $INFO DB_PASS = (redacted)\n"


printf "\n$INFO Check database (read only)\n"
printf "────────────────────────────────────────────────────────\n"

stop_containers 0 1

start_postgres 1 1

printf "$INFO Checking for UNIQUE constraints violations...\n"
QUERY="
SELECT
    indrelid::regclass AS table_name,
    string_agg(quote_ident(a.attname), ',') AS columns
FROM pg_index i
JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
WHERE i.indisunique
  AND NOT i.indisprimary
  AND indrelid::regclass::text NOT LIKE 'pg_%'
  AND indrelid::regclass::text NOT LIKE 'sql_%'
GROUP BY i.indrelid, i.indexrelid;"

RESULTS=$(docker compose exec -T \
    -e PGUSER="$DB_USER" \
    -e PGDATABASE="$DB_NAME" \
    postgres psql -t -A -F "|" -c "$QUERY")

if [ -z "$RESULTS" ]; then
    printf "  └ $ERROR No unique index found in database (there should be !)\n"
    stop_containers 0
    exit 1
fi

VIOLATION_FOUND=false

while IFS="|" read -r table columns; do
    table=$(echo "$table" | tr -d '\r')
    columns=$(echo "$columns" | tr -d '\r')

    CHECK_QUERY="SELECT count(*) FROM (SELECT $columns FROM \"$table\" GROUP BY $columns HAVING count(*) > 1) AS duplicates;"
    DUPLICATE_COUNT=$(docker compose exec -T \
        -e PGUSER="$DB_USER" \
        -e PGDATABASE="$DB_NAME" \
        postgres psql -t -A -c "$CHECK_QUERY" < /dev/null)

    if [ "$DUPLICATE_COUNT" -gt 0 ]; then
        printf "    └ $ERROR Table '$table' on unique group ($columns) : $DUPLICATE_COUNT duplicated set(s).\n"
        VIOLATION_FOUND=true
    fi

done <<< "$RESULTS"

if [ "$VIOLATION_FOUND" = false ]; then
    printf "└ $OK No violation detected.\n"
else
    printf "└ $ERROR Violation(s) detected.\n"

    stop_containers 0

    printf "────────────────────────────────────────────────────────\n"
    echo "[IMPORTANT]"
    echo "You must fix these violations before attempting migration."
    echo "Please report them on CRCON Discord"
    echo "(don't forget to copy/paste the violation details)"
    echo ""
    echo "Most usual error case is \"player_names.unique_name_steamid\""
    echo "Fix : 1. MAKE A BACKUP of your 'db_data/' folder."
    echo "      2. Execute this command while being in CRCON folder :"
    echo ""
    echo "docker compose exec postgres psql -U rcon -d rcon -c \"DELETE FROM public.player_names WHERE id NOT IN (SELECT MAX(id) FROM public.player_names GROUP BY playersteamid_id, name);\""
    printf "────────────────────────────────────────────────────────\n"

    exit 1
fi


printf "\n$INFO Backup\n"
printf "────────────────────────────────────────────────────────\n"

stop_containers 1 1

# Storage availability

printf "$INFO Verify storage availability...\n"
PHYSICAL_DATA_SIZE_KB=$(sudo du -sk "$DATA_DIR" | awk '{print $1}')
printf "└ $INFO Estimated database size on disk: $((PHYSICAL_DATA_SIZE_KB / 1024)) MB.\n"

REQUIRED_SPACE_KB=$((PHYSICAL_DATA_SIZE_KB + (PHYSICAL_DATA_SIZE_KB / 10)))
printf "  └ $INFO Migration process needs $((REQUIRED_SPACE_KB / 1024)) MB free.\n"

AVAILABLE_SPACE_KB=$(df -k "$DATA_DIR" | awk 'NR==2 {print $4}')
if [ "$AVAILABLE_SPACE_KB" -lt "$REQUIRED_SPACE_KB" ]; then
    printf "    └ $ERROR Only $((AVAILABLE_SPACE_KB / 1024)) MB are available.\n"
    exit 1
else
    printf "    └ $OK $((AVAILABLE_SPACE_KB / 1024)) MB are available.\n"
fi

# Backup $ENV_FILE
printf "$INFO Create $ENV_FILE backup... "
BACKUP_ENV=".env_v${CURRENT_VER}_backup_$(date +%Y%m%d_%H%M%S)"
if sudo cp "$ENV_FILE" "$BACKUP_ENV"; then printf "$OK\n"; else printf "$ERROR\n"; exit 1; fi

# Backup $DATA_DIR
printf "$INFO Create $DATA_DIR backup... "
BACKUP_DIR="./db_data_v${CURRENT_VER}_backup_$(date +%Y%m%d_%H%M%S)"
if sudo mv "$DATA_DIR" "$BACKUP_DIR"; then printf "$OK\n"; else printf "$ERROR\n"; exit 1; fi


printf "\n$INFO Prepare migration\n"
printf "────────────────────────────────────────────────────────\n"

# Create a new $DATA_DIR folder
printf "$INFO Create a new '$DATA_DIR' folder... "
if sudo mkdir "$DATA_DIR"; then printf "$OK\n"; else printf "$ERROR\n"; rollback; exit 1; fi

# Give $DATA_DIR ownership to postgres user/group
printf "$INFO Give '$DATA_DIR' folder ownership to postgres:postgres... "
if sudo chown -R 999:999 "$DATA_DIR"; then printf "$OK\n"; else printf "$ERROR\n"; rollback; exit 1; fi


printf "\n$INFO Start migration\n"
printf "────────────────────────────────────────────────────────\n"

# Migration script
UPGRADE_SCRIPT=$(cat <<-'EOF'
    set -e

    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq postgresql-${CURRENT_VER_ENV} > /dev/null

    chown -R postgres:postgres /var/lib/postgresql/old /var/lib/postgresql/new

    gosu postgres sh -e -c "
        cd /var/lib/postgresql/new
        printf '%s' \"\$MIGRATION_PASS\" > /tmp/pg_pass

        /usr/lib/postgresql/${TARGET_VER_ENV}/bin/initdb \
            -D /var/lib/postgresql/new \
            -U \"\$MIGRATION_USER\" \
            --pwfile=/tmp/pg_pass \
            --no-data-checksums \
            -A trust > /dev/null

        /usr/lib/postgresql/${TARGET_VER_ENV}/bin/pg_upgrade \
            -d /var/lib/postgresql/old \
            -D /var/lib/postgresql/new \
            -b /usr/lib/postgresql/${CURRENT_VER_ENV}/bin \
            -B /usr/lib/postgresql/${TARGET_VER_ENV}/bin \
            -U \"\$MIGRATION_USER\" > /dev/null

        echo 'host all all all scram-sha-256' >> /var/lib/postgresql/new/pg_hba.conf

        rm /tmp/pg_pass
    "
EOF
)

MIGRATION_LOG=$(mktemp)

run_with_spinner "Migrating data from v$CURRENT_VER to v$TARGET_VER" "$MIGRATION_LOG" \
    docker run --rm \
        -v "$(pwd)/$BACKUP_DIR:/var/lib/postgresql/old" \
        -v "$(pwd)/$DATA_DIR:/var/lib/postgresql/new" \
        -e "MIGRATION_USER=$DB_USER" \
        -e "MIGRATION_PASS=$DB_PASS" \
        -e "CURRENT_VER_ENV=$CURRENT_VER" \
        -e "TARGET_VER_ENV=$TARGET_VER" \
        --entrypoint /bin/sh \
        "postgres:$TARGET_VER" -c "$UPGRADE_SCRIPT"

if [ $? -ne 0 ]; then
    printf "────────────────────────────────────────────────────────\n"
    printf "$INFO Migrating data from v$CURRENT_VER to v$TARGET_VER... $ERROR\n"
    if [ -s "$MIGRATION_LOG" ]; then
        printf "  └ Details:\n"
        sed 's/^/      /' "$MIGRATION_LOG"
    fi
    rm -f "$MIGRATION_LOG"
    printf "$INFO Don't worry : your original data is safe and is about to be restored.\n"
    printf "────────────────────────────────────────────────────────\n"
    rollback
    exit 1
fi

rm -f "$MIGRATION_LOG"
printf "$INFO Migrating data from v$CURRENT_VER to v$TARGET_VER... $OK\n"


printf "\n$INFO Launch post-upgrade maintenance operations\n"
printf "────────────────────────────────────────────────────────\n"

# Update .env
printf "$INFO Set POSTGRES_IMAGE to \"$TARGET_IMAGE\" in '$ENV_FILE'... "
if sed -i "s|POSTGRES_IMAGE=.*|POSTGRES_IMAGE=$TARGET_IMAGE|" "$ENV_FILE"; then printf "$OK\n"; else printf "$ERROR\n"; rollback; exit 1; fi
echo ""

# Start postgres
start_postgres 1 1

# Refresh collation
printf "$INFO Refresh collation versions... "

COLLATION_ERROR=$(
    docker compose exec -T \
        -e PGUSER="$DB_USER" \
        -e PGDATABASE="postgres" \
        postgres psql \
        -v db_name="$DB_NAME" \
        2>&1 1>/dev/null <<-'SQL'
            UPDATE pg_database
                SET datcollversion = (
                    SELECT collversion
                    FROM pg_collation
                    WHERE collname = 'default'
                )
                WHERE datcollversion IS NOT NULL;
            ALTER DATABASE :"db_name" REFRESH COLLATION VERSION;
            ALTER DATABASE postgres REFRESH COLLATION VERSION;
            SELECT pg_reload_conf();
SQL
)

if [ $? -ne 0 ]; then
    printf "$ERROR\n"
    printf "  └ psql error: %s\n" "$COLLATION_ERROR"
else
    printf "$OK\n"
fi

# PostgreSQL 15 revoked the default CREATE privilege on the public schema from the PUBLIC role.
# Note : DB_USER must be superuser ('rcon' should be by default)
printf "$INFO Add '$DB_USER' user permissions on 'public' SCHEMA... "

GRANT_ERROR=$(
    docker compose exec -T \
        -e PGUSER="$DB_USER" \
        -e PGDATABASE="$DB_NAME" \
        postgres psql \
        -v db_user="$DB_USER" \
        2>&1 1>/dev/null <<-'SQL'
            GRANT CREATE, USAGE ON SCHEMA public TO :db_user;
SQL
)

if [ $? -ne 0 ]; then
    printf "$ERROR\n"
    printf "  └ psql error: %s\n" "$GRANT_ERROR"
    rollback
    exit 1
fi

printf "$OK\n"

# Refresh stats
VACUUM_LOG=$(mktemp)
run_with_spinner "Optimizing database statistics" "$VACUUM_LOG" \
    docker compose exec -T \
        -e PGUSER="$DB_USER" \
        postgres vacuumdb --all --analyze-in-stages

if [ $? -ne 0 ]; then
    printf "$INFO Optimizing database statistics... $ERROR\n"
    [ -s "$VACUUM_LOG" ] && printf "  └ vacuumdb error: %s\n" "$(cat "$VACUUM_LOG")"
    rm -f "$VACUUM_LOG"
    rollback
    exit 1
fi
rm -f "$VACUUM_LOG"
printf "$INFO Optimizing database statistics... $OK\n"

# Upgrade password hash to SCRAM-SHA-256
printf "$INFO Upgrade '$DB_USER' password encryption to SCRAM-SHA-256... "

ALTER_ERROR=$(
    docker compose exec -T \
        -e PGUSER="$DB_USER" \
        -e PGDATABASE="postgres" \
        -e PGPASSWORD="$DB_PASS" \
        postgres psql \
        -v db_user="$DB_USER" \
        -v db_pass="$DB_PASS" \
        2>&1 1>/dev/null <<-'SQL'
            ALTER USER :db_user WITH PASSWORD :'db_pass';
SQL
)

if [ $? -ne 0 ]; then
    printf "$ERROR\n"
    printf "  └ psql error: %s\n" "$ALTER_ERROR"
    rollback
    exit 1
fi

printf "$OK\n"

# Complete pg_dump
DUMP_LOG=$(mktemp)
run_with_spinner "Verifying data integrity (pg_dump)" "$DUMP_LOG" \
    docker compose exec -T \
        -e PGUSER="$DB_USER" \
        -e PGDATABASE="$DB_NAME" \
        postgres pg_dump

if [ $? -ne 0 ]; then
    printf "$INFO Verifying data integrity (pg_dump)... $ERROR\n"
    [ -s "$DUMP_LOG" ] && printf "  └ pg_dump error: %s\n" "$(cat "$DUMP_LOG")"
    rm -f "$DUMP_LOG"
    rollback
    exit 1
fi
rm -f "$DUMP_LOG"
printf "$INFO Verifying data integrity (pg_dump)... $OK\n"
echo ""

# Stop postgres
stop_containers 0

# Start CRCON
start_containers 0

printf "────────────────────────────────────────────────────────\n"
printf "$OK Database has been upgraded from v$CURRENT_VER to v$TARGET_VER\n"
printf "────────────────────────────────────────────────────────\n"
if [[ -f "$BACKUP_ENV" || ( -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ) ]]; then
    if [ -f "$BACKUP_ENV" ]; then
        printf "$INFO v$CURRENT_VER '$ENV_FILE' file backup is: '$BACKUP_ENV'\n"
    fi
    if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
        printf "$INFO v$CURRENT_VER database folder backup is: '$BACKUP_DIR'\n"
    fi
    printf "$INFO Make sure everything works as intended before deleting backups.\n"
fi
printf "────────────────────────────────────────────────────────\n"
echo ""

exit 0