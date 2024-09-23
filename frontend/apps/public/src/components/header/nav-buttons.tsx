import Link from 'next/link';
import siteConfig from '../../utils/siteConfig';
import { SimpleIcon } from '@shared/components/simple-icon';
import { siGithub } from 'simple-icons';
import { ModeToggle } from '@shared/components/theme-toggle';

export function NavButtons() {
  return (
    <div className="ml-auto flex items-center space-x-1 [&>*]:size-8">
      <Link
        href={siteConfig.crconGitUrl}
        className="border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 dark:fill-foreground"
      >
        <SimpleIcon icon={siGithub} size={20} />
      </Link>
      <ModeToggle />
    </div>
  );
}
