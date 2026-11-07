import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

for (const path of ['/', '/getting-started/', '/generated/cli-usage/', '/generated/desktop-sidecar/']) {
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
  const select = page.locator('header starlight-theme-select select');
  await select.selectOption('dark');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.getByRole('link', { name: '开始使用' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await select.selectOption('light');
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
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
