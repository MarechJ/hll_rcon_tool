# CRCON GUI

A React-based web interface displaying match results and player statistics for community-hosted Hell Let Loose game servers.

## Tech Stack

- React 18
- Typescript
- Vite
- React Router 6
- Tanstack Query 5
- Tanstack Table 8
- shadcn-ui
- Tailwind CSS

## Prerequisites

- Node.js (v18 or higher)
- NPM package manager
- A running CRCON server instance

## Setup

1. Clone the repository
2. Navigate to the project directory

```bash
cd rcongui_public
```

3. Install dependencies:

```bash
npm install
```

3. Create a `.env.development.local` file in the root directory from the `example.env` file:

```bash
cp example.env .env.development.local
```

4. Set the following variables in the `.env` file:

You don't necessarily need to change anything here.

- `VITE_CRCON_API_URL`: The API endpoint of your CRCON server

If you don't have your own server, you should be able to use the URL of any other CRCON managed HLL server e.g. `stats.hll-community.com`

5. Start the development server:

```bash
npm run dev
```

## Other commands

Build and preview the production version:

```bash
npm run preview
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes and commit them
4. Push your changes to your fork
5. Create a pull request
