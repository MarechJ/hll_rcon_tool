## Vite-React-TS-Tailwind-Starter

Choosing a technology stack is a very subjective matter, if you happen to like using `Vite`, `Tailwind`, `TS` and `shadcn ui` and more to build React SPA applications, then give it a try.

## Run


```sh
yarn
yarn dev
```

We prefer `Yarn` as package manager, If you want to use `pnpm` or `npm`, feel free to use


## Tech Stack

- [vite](https://vitejs.dev/)
- [react](https://reactjs.org/)
- [shadcn ui](https://ui.shadcn.com/)
- [react-i18next](https://github.com/i18next/react-i18next)
- [react-lucide](https://lucide.dev/)
- [transmart](https://github.com/Quilljou/transmart)
- [react-query](https://tanstack.com/query/latest/)
- [tailwindcss](https://tailwindcss.com/)
- [less](http://lesscss.org/)
- [postcss](https://postcss.org/)
- [react-router-dom](https://reactrouter.com/en/6.16.0)
- [eslint](https://eslint.org/)/[stylelint](https://stylelint.io/)
- [prettier](https://prettier.io/)
- [svgr](https://react-svgr.com/)
- [editorconfig](https://editorconfig.org/)
- [husky](https://typicode.github.io/husky/#/)/[lint-staged](https://github.com/okonet/lint-staged)
- [commitlint](https://commitlint.js.org/)


## Project Structure

```sh
src
├── app.tsx     # App entry
├── assets      # Assets for images, favicon etc
├── components  # React components
├── hooks       # React hooks
├── i18n        # i18n files
├── lib         # Utils、tools、services
├── main.tsx    # File entry
├── pages       # One .tsx per page
├── router.tsx  # Routers
├── styles      # Less files
├── types       # Typescript types
└── vite-env.d.ts
```

## Deploy

[Cloudflare Pages](https://pages.cloudflare.com/) is my first option to deploy React App，follow [this documentation](https://developers.cloudflare.com/pages/framework-guides/deploy-a-react-site/#deploying-with-cloudflare-pages) to deploy your site. Don't forget build directory should	choose `dist`

[Vercel](https://pages.cloudflare.com/) is a good option too，Go to [Vercel](https://vercel.com/new) and link to your Git Repo

Enjoy building.


## Related

- [Next Starter](https://github.com/Quilljou/next-ts-tailwind-starter)

- [React Starter](https://github.com/Quilljou/vite-react-ts-tailwind-starter)

- [Figma Starter](https://github.com/Quilljou/figma-react-tailwind-starter)
