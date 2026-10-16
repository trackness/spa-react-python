import { expect, test } from "@playwright/test";

test("the home page shows the App is ready", async ({ page }) => {
	await page.goto("/");

	await expect(page.getByText("The App is ready.")).toBeVisible();
});
