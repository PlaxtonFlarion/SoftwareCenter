import { readFileSync } from 'node:fs';
import { defineConfig } from 'astro/config';
import { rehypeHeadingIds, unified } from '@astrojs/markdown-remark';
import starlight from '@astrojs/starlight';
import legacyAnchors from './src/plugins/legacy-anchors';

const { entries } = JSON.parse(readFileSync(new URL('./docs_manifest.json', import.meta.url), 'utf8'));
const product = JSON.parse(readFileSync(new URL('./src/generated/product.json', import.meta.url), 'utf8'));
const sections = ['使用指南', '工具与集成', '命令参考', '开发者'];

export default defineConfig({
  site: 'https://www.appserverx.com',
  outDir: './site',
  trailingSlash: 'always',
  markdown: { processor: unified({ rehypePlugins: [rehypeHeadingIds, legacyAnchors] }) },
  integrations: [
    starlight({
      title: product.name,
      description: `${product.name} 使用文档：安装、交互、工具集成与工程任务指南。`,
      locales: { root: { label: '简体中文', lang: 'zh-CN' } },
      favicon: '/favicon.svg',
      customCss: ['./src/styles/docs.css'],
      components: {
        Header: './src/components/Header.astro',
        SiteTitle: './src/components/SiteTitle.astro',
        ThemeSelect: './src/components/ThemeControl.astro',
        ThemeProvider: './src/components/ThemeProvider.astro',
        PageTitle: './src/components/PageHeading.astro',
        Hero: './src/components/HomeHero.astro',
        Footer: './src/components/Footer.astro',
      },
      sidebar: [
        { label: '快速开始', link: '/getting-started/' },
        ...sections.map((section) => ({
          label: section,
          collapsed: section === '开发者',
          items: [
            ...(section === '使用指南' ? [{ label: '选择运行方式', link: '/capabilities/' }] : []),
            ...(section === '命令参考' ? [{ label: '常用命令速查', link: '/reference/' }] : []),
            ...entries.filter((entry) => entry.section === section).map((entry) => ({
              label: entry.label,
              link: `/generated/${entry.target.replace(/\.md$/, '')}/`,
            })),
          ],
        })),
      ],
      tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 3 },
      pagination: true,
      disable404Route: true,
      credits: false,
    }),
  ],
});
