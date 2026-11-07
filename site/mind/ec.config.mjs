import { defineEcConfig } from '@astrojs/starlight/expressive-code';
import { visit } from 'unist-util-visit';

export default defineEcConfig({
  themes: ['github-light', 'github-dark'],
  plugins: [{
    name: 'Accessible code blocks',
    hooks: {
      postprocessRenderedBlock: ({ renderData }) => {
        visit(renderData.blockAst, 'element', (node) => {
          if (node.tagName !== 'pre') return;
          node.properties.tabIndex = 0;
        });
      },
    },
  }],
  styleOverrides: {
    borderRadius: '0.5rem',
    borderColor: 'var(--sl-color-gray-5)',
    codeBackground: 'var(--code-surface)',
    codeFontFamily: 'var(--sl-font-mono)',
    codeFontSize: '0.875rem',
    codeLineHeight: '1.7',
    frames: {
      frameBoxShadowCssValue: 'none',
      terminalBackground: 'var(--code-surface)',
      terminalTitlebarBackground: 'var(--surface-raised)',
      terminalTitlebarBorderBottomColor: 'var(--sl-color-gray-5)',
    },
  },
});
