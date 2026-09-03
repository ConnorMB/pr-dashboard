// turns owner/repo or full github url into {owner, name}
export function parseRepoInput(value) {
  const trimmed = value.trim();

  const urlMatch = trimmed.match(/github\.com\/([^/\s]+)\/([^/\s]+?)(?:\.git)?\/?$/);
  if (urlMatch) {
    return { owner: urlMatch[1], name: urlMatch[2] };
  }

  const shorthandMatch = trimmed.match(/^([^/\s]+)\/([^/\s]+)$/);
  if (shorthandMatch) {
    return { owner: shorthandMatch[1], name: shorthandMatch[2] };
  }

  return null;
}