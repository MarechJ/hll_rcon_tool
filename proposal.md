# Introduction

**tl;dr**: Add calendar popups (similar to the control you see when filtering historical logs by date) to pick an expiration date/time when adding a VIP, and shortcuts (+30 days from now, +60 days, etc.) and another service that will remove expired VIPs periodically (hourly or whatever).


VIP access to community servers is a primary (perhaps the primary method) of funding community servers. Some communities also use VIP to reward and increasing seeding activity. However VIP status is tracked on the game server itself and consists of a Steam ID and a free form text field for the players name, and VIP status must be updated manually by server admins.

Due to the manual work required to update VIPs for players who do not have permanent VIP, many communities require players to pay for VIP for a calendar month, regardless of the start date and remove (or rebill) at the start of each month. This proposal is to modify Community RCON to allow for VIPs to be added with an expiration date and have them be automatically removed.

This would allow for players to purchase VIP access at any time of the month without creating any more work than adding a VIP by the regular method, and would eliminate the work required to remove VIPs when their payment period has ended. This would also allow admins to easily re-up (at any point in the billing period) a users VIP status for an additional 30, 60, etc. days.

# Current Methods of Adding/Removing VIPs in RCON
## Adding/Removing an Individual
* History > Players
    * Individual players are shown and their VIP status can be toggled on or off by clicking on the star.
* Settings > Manage VIPs
    * All players that have currently have VIP are shown in the `Manage VIPs` drop down, and new players can be added one at a time.
## Bulk Uploading
* Settings > Manage VIPs
    * Upload VIPs
        * Admins can upload a file of Steam IDs/names, anyone who is not a VIP has their status removed, and all players in the list have it added
## Removing All VIPs
* All old VIPs are removed when an admin uploads a VIP file
* There is a `do_remove_all_vips` command in `rcon.extended_commands.py` which is accessible through auto settings and is also exposed as an API method

# Backwards Compatibility

Any changes to Community RCON that allow for expiring VIPs should still allow for indefinite VIP access for players and should be totally optional to use. It should also not cause any breaking changes that force admins to have to update their VIP list if they upgrade to a release that has expiring VIPs, or break anything if they downgrade.

Admins should also be able to download a VIP list from a newer version of Community RCON and upload it to an older one without issue.

# Proposed New Methods of Adding Expiring VIPs

* Add a calendar popup that will show when adding VIP through the History > Players view that will allow an admin to pick an exact date/time VIP should expire (or never) and some quick shortcut dates (+30 days, +60 days, +90 days, 1 year).

* Add a third field to `Manage VIPs` section of RCON Settings that will display the same calendar control used above when clicked, and in the field show the expiration date (or infinity) for indefinite VIPs

* Add a checkbox to `Manage VIPs` that will enable attempting to parse [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) dates from names on VIP upload, and will add dates to names on download.

# Implementation Details

You can stop reading here if you don't care how I plan on actually implementing the feature.

**tl;dr** add a new table to track expiration dates, update UI controls to allow admins to input a date when adding VIP, add a service to remove expired VIPs and update the `Manage VIPs` UI to allow inputting a date and control whether or not an uploaded/downloaded VIP file will download with dates or parse dates on upload.

# Database Changes

1. Add a new table `player_vip` with the following fields/types.
    1. `id` - `integer` - `primary key` 
    2. `steam_id_64` - `character varying` - `foreign key` to table `steam_id_64`
    3. `expiration` - `timestamp with timezone`

The Postgres [timestamp with timezone type](https://www.postgresql.org/docs/9.1/datatype-datetime.html) stores a date and time with time zone information and has much more precision (1 microsecond) than required. It also includes a handy shortcut `infinity` that is treated as `later than all other time stamps` which we can use for VIPs that don't expire without needing special comparison logic or nulled fields.

# UI Changes

1. Add a calendar control (identical to the date picker used on the historical log view) but with an additional set of buttons for discrete time periods as shortcuts.
    1. This expanded control would be used anywhere you can add an individual VIP (currently the Player view on the History view when clicking the star and on the settings page).
    2. The shortcut buttons would add the indicated unit of time to the players current expiration date.
        1. Choosing indefinite would set it to postgres `infinity`.
        2. If the player does not already have an expiration date set it would add the unit of time to the users current system time.
2. Update the player card UI to show the players expiration timestamp if they're a VIP.
    1. Also show this expiration date on the date picker for user convenience.
3. Add a third field to the VIP addition control on RCON Settings.
    1. Users with an expiration set would have show the timestamp as an ISO 8601 string
    2. Indefinite VIPs would show `infinity`
3. Add a checkbox to the `Manage VIP` control to handle backwards compatibility for uploading/downloading VIPs
4. Add VIP status/expiration time (not editable) to the single player view

# Bulk Upload/Download Considerations

Communities can use the VIP download feature when migrating to a new instance of Community RCON, to backup their VIP lists, etc. Downloading the VIP list and immediately re-uploading it should not lose any information or cause there to be any inconsistencies.

The added checkbox (off by default) will control whether or not we download expiration dates, or attempt to parse them from the uploaded list.

Downloading the VIP list will append the expiration date as an ISO 8601 string to the end of the player name if they have a record in `player_vip`

Uploading a VIP list will attempt to parse a valid timestamp from each player's name when uploading and if found will set the expiration date to this timestamp and strip this timestamp from the player's name.

If we can't parse a valid date from a player's name, set to indefinite

Since `infinity` is a potential real player name, or partial player name, store indefinite VIPs as a sentinel date (say a century in the future) that is equivalent to indefinite for practical purposes.

If someone sets a players name to a parseable timestamp, things will probably break but admins can just not do this.

# Logging / Webhooks

Any updates that are done through the API are automatically logged.  Database operations will be logged in the `RecordedRcon` methods. Removing expired VIPs will be logged in the optional service.

Adding or removing a VIP should include the new expiration date or the previous one if it's being removed (allows for easy data recovery if someone is accidentally removed).

# Timezones

All timestamps will be stored in postgres as UTC timestamps, any incoming date/times from the front end will include the users system time UTC offset so we can convert their actual desired timestamp properly.

i.e. if a UTC -6 user submits 2022-10-15 12:00:00 it is properly stored as 2022-10-15 18:00:00+00:00 instead of blindly converting the incoming timestamp to UTC as is and making it 6 hours earlier than they expect.

# Database Operations

* Adding VIP status to a player creates a record for them in `player_vip`
* Removing VIP status from a player deletes their record for them in `player_vip`
* Updating a players VIP expiration date modifies their record in `player_vip`

# Removing Expired VIPs

This will add a configurable service that will be controlled on the RCON settings page like other services and run every N minutes (user configured) and remove any players that have a record in `player_vip` that is older than the current time.

If a player has VIP but has no record in `player_vip` they will be treated as having indefinite VIP for backwards compatibility but a warning will be logged

Removals will be done through recorded RCON commands and logged/discord audited.

# Hooking into Recorded RCON VIP Commands

This will override `do_add_vip` and `do_remove_vip` in `rcon.recorded_commands` to handle inserting/updating/deleting `player_vip` records, strip out the additional information (expiration date) and delegate to the super classes to finish.

# Undecided Details
* Should expiration dates show on a players information team view?
    * Seems unneccessary to me