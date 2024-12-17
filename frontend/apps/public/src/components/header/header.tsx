import { MainNav } from './main-nav';
import { ServerName } from '../server-name';
import { MobileNav } from './mobile-nav';
import { NavButtons } from './nav-buttons';
import { ServerStatus } from '../server-status';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="border-b">
        <div className="container px-2 md:px-8 flex h-14 max-w-screen-2xl items-center">
          <MainNav className="mx-6" />
          <MobileNav />
          <div className="flex flex-grow justify-end items-center px-4 overflow-hidden">
            <ServerStatus />
            <span className='ml-2 truncate'>
              <ServerName />
            </span>
          </div>
          <NavButtons />
        </div>
      </div>
    </header>
  );
}
