// Start with the release current when this fork was configured; then follow every new release.
const firstPublishedAt = '2026-10-20T07:01:34Z';
module.exports = async ({ github, context, core }) => {
  const upstream = { owner: 'Meloong-Git', repo: 'PCL' };
  const releases = await github.paginate(github.rest.repos.listReleases, {
    ...upstream, per_page: 100
  });
  const own = await github.paginate(github.rest.repos.listReleases, {
    ...context.repo, per_page: 100
  });
  const pending = releases
    .filter(r => !r.draft && r.published_at >= firstPublishedAt)
    .sort((a, b) => a.published_at.localeCompare(b.published_at))
    .filter(r => !own.some(f =>
      f.tag_name === `fork-${r.tag_name}` && !f.draft &&
      f.body?.includes(`<!-- pcl-upstream-release:${r.id} -->`) &&
      ['.exe', '.zip', 'SHA256SUMS.txt'].every(suffix =>
        f.assets.some(a => a.name.endsWith(suffix) && a.size > 0))))
    .slice(0, 10)
    .map(r => ({
      tag: r.tag_name, id: r.id, prerelease: r.prerelease,
      url: r.html_url, published_at: r.published_at
    }));
  core.setOutput('matrix', JSON.stringify({ include: pending }));
  core.setOutput('pending', String(pending.length > 0));
  core.info(`Pending upstream releases: ${pending.map(r => r.tag).join(', ') || 'none'}`);
};
