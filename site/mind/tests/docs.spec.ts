import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Route } from '@playwright/test';
import manifest from '../docs_manifest.json' with { type: 'json' };
import { readingThemes } from '../src/reading-themes';

for (const path of ['/', '/getting-started/', '/capabilities/', '/reference/', '/generated/cli-usage/', '/generated/desktop-sidecar/']) {
  test(`${path} 阅读布局与无障碍`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    const response = await page.goto(path);
    expect(response?.status()).toBe(200);
    await expect(page.locator('h1')).toHaveCount(1);
    await expect(page.locator('html')).toHaveAttribute('lang', 'zh-CN');
    await expect(page.locator('site-search button[data-open-modal]')).toBeEnabled();
    const width = await page.evaluate(() => ({
      document: document.documentElement.scrollWidth,
      viewport: document.documentElement.clientWidth,
    }));
    expect(width.document).toBeLessThanOrEqual(width.viewport);
    const accessibility = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    expect(accessibility.violations).toEqual([]);
    expect(errors).toEqual([]);
  });
}

for (const query of ['审批', 'MCP', 'Ctrl+C']) {
  test(`搜索 ${query} 并打开正文`, async ({ page }) => {
    await page.goto('/');
    const open = page.locator('button[data-open-modal]');
    await expect(open).toBeEnabled();
    await page.keyboard.press('Control+k');
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
    await dialog.locator('.pagefind-ui__search-input').fill(query);
    const result = dialog.locator('.pagefind-ui__result-link').first();
    await expect(result).toBeVisible();
    await expect(dialog).not.toContainText('No results');
    const href = await result.getAttribute('href');
    expect(href).toBeTruthy();
    await result.click();
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    expect(new URL(page.url()).pathname).not.toBe('/');
  });
}

test('键盘关闭搜索后恢复焦点，空结果可重新搜索', async ({ page }) => {
  await page.goto('/');
  const open = page.locator('button[data-open-modal]');
  await expect(open).toBeEnabled();
  await open.focus();
  await page.keyboard.press('Enter');
  const dialog = page.getByRole('dialog');
  await dialog.locator('.pagefind-ui__search-input').fill('"qzvxjkpwrytnhbfz"');
  await expect(dialog.locator('.pagefind-ui__message')).toContainText('没有');
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();
  await expect(open).toBeFocused();
  await page.keyboard.press('Enter');
  await dialog.locator('.pagefind-ui__search-input').fill('会话');
  await expect(dialog.locator('.pagefind-ui__result-link').first()).toBeVisible();
});

test('主题选择与跨页面持久化', async ({ page }) => {
  await page.goto('/');
  const themes = page.locator('header reading-theme');
  const surfaces = new Set<string>();
  for (const theme of readingThemes) {
    await themes.getByRole('button', { name: '选择阅读主题' }).click();
    await expect(themes.getByRole('group', { name: '阅读主题选项' }).getByRole('button')).toHaveCount(readingThemes.length);
    await themes.getByRole('button', { name: theme.name, exact: true }).click();
    await expect(page.locator('html')).toHaveAttribute('data-reading-theme', theme.id);
    await expect(page.locator('html')).toHaveAttribute('data-theme', theme.mode);
    await expect(themes.getByRole('button', { name: '选择阅读主题' })).toBeFocused();
    surfaces.add(await page.locator('html').evaluate((element) => getComputedStyle(element).getPropertyValue('--sl-color-black')));
    await page.reload();
    await expect(page.locator('html')).toHaveAttribute('data-reading-theme', theme.id);
  }
  expect(surfaces.size).toBe(readingThemes.length);
  const lastTheme = readingThemes.at(-1);
  if (!lastTheme) throw new Error('阅读主题清单为空');
  await page.getByRole('link', { name: '开始使用' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-reading-theme', lastTheme.id);
  await themes.getByRole('button', { name: '选择阅读主题' }).click();
  await expect(themes.getByRole('button', { name: lastTheme.name, exact: true })).toHaveAttribute('aria-pressed', 'true');
  await page.keyboard.press('Escape');
  await expect(themes.locator('.theme-panel')).toBeHidden();
  await expect(themes.getByRole('button', { name: '选择阅读主题' })).toBeFocused();
});

test('首次访问按系统外观选择主题，减少动态效果时不执行动画', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light', reducedMotion: 'reduce' });
  await page.goto('/getting-started/');
  await expect(page.locator('html')).toHaveAttribute('data-reading-theme', 'dawn');
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-reading-theme', 'forest');
  const themes = page.locator('header reading-theme');
  await themes.getByRole('button', { name: '选择阅读主题' }).click();
  await themes.getByRole('button', { name: '落日熔金', exact: true }).click();
  await expect(page.locator('html')).toHaveAttribute('data-reading-theme', 'amber');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  expect(await page.evaluate(() => document.getAnimations().length)).toBe(0);
});

test('短屏主题面板可用键盘滚动到最后一款', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 480 });
  await page.goto('/getting-started/');
  const themes = page.locator('header reading-theme');
  const trigger = themes.getByRole('button', { name: '选择阅读主题' });
  await trigger.click();
  const lastTheme = readingThemes.at(-1);
  if (!lastTheme) throw new Error('阅读主题清单为空');
  for (const theme of readingThemes) {
    await page.keyboard.press('Tab');
    await expect(themes.getByRole('button', { name: theme.name, exact: true })).toBeFocused();
  }
  await expect(themes.getByRole('button', { name: lastTheme.name, exact: true })).toBeInViewport();
  await page.keyboard.press('Enter');
  await expect(page.locator('html')).toHaveAttribute('data-reading-theme', lastTheme.id);
  await expect(themes.locator('.theme-panel')).toBeHidden();
  await expect(trigger).toBeFocused();
});

test('主题动画播放期间仍可再次打开选择器', async ({ page }) => {
  await page.goto('/generated/mcp-server/');
  await page.addStyleTag({ content: ':root[data-theme-transition]::view-transition-new(reading-content) { animation-duration: 2s !important; }' });
  const themes = page.locator('header reading-theme');
  const trigger = themes.getByRole('button', { name: '选择阅读主题' });
  await trigger.click();
  await themes.getByRole('button', { name: '落日熔金', exact: true }).click();
  await expect.poll(() => page.evaluate(() => document.getAnimations().some(
    (animation) => animation instanceof CSSAnimation && animation.animationName === 'theme-dissolve',
  ))).toBe(true);
  const bounds = await trigger.boundingBox();
  if (!bounds) throw new Error('主题入口不可见');
  await page.mouse.click(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2);
  await expect(themes.locator('.theme-panel')).toBeVisible();
  await themes.getByRole('button', { name: '星河入梦', exact: true }).click();
  await expect(page.locator('html')).toHaveAttribute('data-reading-theme', 'nebula');
  await expect(page.locator('html')).not.toHaveAttribute('data-theme-transition', '');
  await expect(trigger).toBeFocused();
});

test('快照提交前改回原主题时保留最后一次选择', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto('/generated/mcp-server/');
  await page.locator('header .theme-trigger').click();
  const result = await page.evaluate(async () => {
    const trigger = document.querySelector<HTMLButtonElement>('header .theme-trigger');
    const forest = document.querySelector<HTMLButtonElement>('header [data-theme-value="forest"]');
    const dawn = document.querySelector<HTMLButtonElement>('header [data-theme-value="dawn"]');
    if (!trigger || !forest || !dawn) throw new Error('主题入口缺失');
    const pending: Promise<void>[] = [];
    const start = document.startViewTransition.bind(document);
    document.startViewTransition = (update) => {
      const transition = start(update);
      pending.push(transition.finished);
      return transition;
    };
    forest.click();
    trigger.click();
    dawn.click();
    await Promise.all(pending);
    return {
      theme: document.documentElement.dataset.readingTheme,
      saved: localStorage.getItem('docs-reading-theme'),
      transitioning: document.documentElement.hasAttribute('data-theme-transition'),
    };
  });
  expect(result).toEqual({ theme: 'dawn', saved: 'dawn', transitioning: false });
});

test('没有快照 API 时可切换并记住显式选择的默认主题', async ({ page }) => {
  await page.addInitScript(() => Object.defineProperty(document, 'startViewTransition', { value: undefined }));
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto('/');
  const themes = page.locator('header reading-theme');
  await themes.getByRole('button', { name: '选择阅读主题' }).click();
  await themes.getByRole('button', { name: '晴岚映雪', exact: true }).click();
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-reading-theme', 'dawn');
  await themes.getByRole('button', { name: '选择阅读主题' }).click();
  await themes.getByRole('button', { name: '星河入梦', exact: true }).click();
  await expect(page.locator('html')).toHaveAttribute('data-reading-theme', 'nebula');
  await expect(page.locator('html')).not.toHaveAttribute('data-theme-transition', '');
});

for (const theme of readingThemes) {
  test(`${theme.name} 首页、正文与主题面板的对比度`, async ({ page }) => {
    await page.goto('/');
    const themes = page.locator('header reading-theme');
    await themes.getByRole('button', { name: '选择阅读主题' }).click();
    await themes.getByRole('button', { name: theme.name, exact: true }).click();
    await expect(page.locator('html')).toHaveAttribute('data-reading-theme', theme.id);
    await themes.getByRole('button', { name: '选择阅读主题' }).click();
    const home = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    expect(home.violations).toEqual([]);
    await page.keyboard.press('Escape');
    await page.getByRole('link', { name: '开始使用', exact: true }).click();
    const document = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    expect(document.violations).toEqual([]);
  });
}

test('全部文档页面保持布局与主题入口一致', async ({ page }) => {
  test.setTimeout(90_000);
  const routes = ['/getting-started/', '/capabilities/', '/reference/', '/generated/catalog/',
    ...manifest.entries.map((entry) => `/generated/${entry.target.replace(/\.md$/, '')}/`)];
  for (const route of routes) {
    await test.step(route, async () => {
      const response = await page.goto(route);
      expect(response?.status()).toBe(200);
      await expect(page.locator('.page-heading h1')).toHaveCount(1);
      await expect(page.locator('h1')).toHaveCount(1);
      await expect(page.locator('header reading-theme .theme-trigger')).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
    });
  }
});

test('搜索快捷入口、清空查询和原位置焦点恢复', async ({ page }) => {
  await page.goto('/');
  const trigger = page.getByRole('link', { name: '开始使用', exact: true });
  await trigger.focus();
  await page.keyboard.press('Control+k');
  const dialog = page.getByRole('dialog');
  const shortcuts = dialog.getByRole('navigation', { name: '常用文档' });
  await expect(shortcuts).toBeVisible();
  const input = dialog.locator('.pagefind-ui__search-input');
  await input.fill('MCP');
  await expect(shortcuts).toBeHidden();
  await dialog.getByRole('button', { name: '清空', exact: true }).click();
  await expect(shortcuts).toBeVisible();
  await input.fill('会话');
  await page.keyboard.press('Escape');
  await expect(trigger).toBeFocused();
  await page.keyboard.press('Control+k');
  await expect(shortcuts).toBeVisible();
  await shortcuts.getByRole('link', { name: '安装与首次配置' }).click();
  await expect(page).toHaveURL(/\/getting-started\/$/);
});

test('窄屏页头操作不重叠且菜单可以打开', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await page.goto('/getting-started/');
  const theme = page.locator('header reading-theme');
  const menu = page.getByRole('button', { name: '菜单', exact: true });
  const themeBounds = await theme.boundingBox();
  const menuBounds = await menu.boundingBox();
  expect(themeBounds).not.toBeNull();
  expect(menuBounds).not.toBeNull();
  if (!themeBounds || !menuBounds) throw new Error('页头操作区域缺失');
  expect(themeBounds.x + themeBounds.width).toBeLessThanOrEqual(menuBounds.x - 4);
  await menu.click();
  await page.getByRole('navigation', { name: '主导航' }).getByRole('link', { name: 'Hooks 配置', exact: true }).click();
  await expect(page).toHaveURL(/\/generated\/hooks\/$/);
});

test('中文章节与旧 OAuth 书签', async ({ page }) => {
  for (const anchor of ['oauth', 'oauth-浏览器登录']) {
    await page.goto(`/generated/cli-usage/#${encodeURIComponent(anchor)}`);
    await expect(page.locator(`[id="${anchor}"]`)).toHaveCount(1);
    const target = page.locator('h3', { hasText: 'OAuth 浏览器登录' }).first();
    await expect(target).toBeInViewport();
  }
});

test('导航展开并进入工具正文', async ({ page, isMobile }) => {
  await page.goto('/getting-started/');
  if (isMobile) await page.locator('button[popovertarget="starlight__sidebar"]').click();
  const navigation = page.getByRole('navigation', { name: '主导航' });
  await navigation.getByRole('link', { name: 'Hooks 配置', exact: true }).click();
  await expect(page).toHaveURL(/\/generated\/hooks\/$/);
  await expect(page.locator('h1')).toHaveText('Hooks 配置');
});

test('宽屏正文行宽与减少动态效果', async ({ page }) => {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/generated/cli-usage/');
  const width = await page.locator('.sl-markdown-content').evaluate((element) => element.getBoundingClientRect().width);
  expect(width).toBeGreaterThanOrEqual(760);
  expect(width).toBeLessThanOrEqual(820);
  await page.goto('/');
  const transition = await page.locator('.guide-link').first().evaluate((element) => getComputedStyle(element).transitionDuration);
  expect(transition).toBe('0s');
});

test('失效页面提供返回入口', async ({ page }) => {
  const response = await page.goto('/missing-document-for-check/');
  expect(response?.status()).toBe(404);
  await expect(page.locator('h1')).toHaveText('页面未找到');
  await page.getByRole('link', { name: '返回文档首页', exact: true }).click();
  await expect(page.locator('.home-hero')).toBeVisible();
});

test('空闲回调不执行时仍可搜索和访问代码区', async ({ page }) => {
  await page.addInitScript(() => { window.requestIdleCallback = () => 1; });
  await page.goto('/generated/desktop-sidecar/');
  const inaccessible = await page.locator('.expressive-code pre').evaluateAll((blocks) => blocks
    .filter((block) => block.scrollWidth > block.clientWidth && block.getAttribute('tabindex') !== '0')
    .map((block) => block.textContent));
  expect(inaccessible).toEqual([]);
  await page.locator('button[data-open-modal]').click();
  const input = page.getByRole('dialog').locator('.pagefind-ui__search-input');
  await expect(input).toBeFocused();
  await input.fill('审批');
  await expect(page.getByRole('dialog').locator('.pagefind-ui__result-link').first()).toBeVisible();
});

test('搜索资源加载失败时可关闭并重新加载页面', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('button[data-open-modal]')).toBeEnabled();
  await page.route('**/ui-core.*.js', (route) => route.abort());
  await page.locator('button[data-open-modal]').click();
  const dialog = page.getByRole('dialog');
  await expect(dialog.getByRole('status')).toContainText('搜索加载失败');
  await expect(dialog.getByRole('button', { name: '重新加载页面' })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(dialog).not.toBeVisible();
  await page.unroute('**/ui-core.*.js');
  await page.locator('button[data-open-modal]').click();
  await dialog.getByRole('button', { name: '重新加载页面' }).click();
  await page.locator('button[data-open-modal]').click();
  await expect(dialog.locator('.pagefind-ui__search-input')).toBeFocused();
});

test('关闭搜索后完成加载不会抢焦点或重复创建输入框', async ({ page }) => {
  await page.goto('/');
  const requests: Route[] = [];
  await page.route('**/ui-core.*.js', (route) => { requests.push(route); });
  const open = page.locator('button[data-open-modal]');
  await open.click();
  const dialog = page.getByRole('dialog');
  await expect(dialog.getByRole('status')).toContainText('正在准备搜索');
  await expect.poll(() => requests.length).toBe(1);
  await dialog.getByRole('button', { name: '关闭搜索' }).click();
  await requests[0].continue();
  await page.unroute('**/ui-core.*.js');
  await expect(page.locator('.pagefind-ui__search-input')).toHaveCount(1);
  await expect(open).toBeFocused();
  await open.click();
  await expect(dialog.locator('.pagefind-ui__search-input')).toBeFocused();
  await expect(dialog.locator('.pagefind-ui__search-input')).toHaveCount(1);
});
