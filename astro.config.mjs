// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { generatedSidebar } from './src/generated/sidebar.mjs';

export default defineConfig({
  site: 'https://colamentos2023.github.io',
  base: '/CSE_Learning_Resource_Hub/',
  integrations: [
    starlight({
      title: 'Control Nexus',
      description: 'A Learning Resource Hub for Control Engineering',
      logo: {
        src: './src/assets/logo.svg',
        alt: 'Control Nexus',
      },
      customCss: ['./src/styles/custom.css'],
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/Colamentos2023/CSE_Learning_Resource_Hub',
        },
      ],
      sidebar: generatedSidebar,
      tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 3 },
      editLink: {
        baseUrl: 'https://github.com/Colamentos2023/CSE_Learning_Resource_Hub/edit/main/',
      },
      lastUpdated: true,
    }),
  ],
});
