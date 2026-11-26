export function isActiveSectionRoute(pathname: string, sectionHref: string): boolean {
  return pathname === sectionHref || pathname.startsWith(`${sectionHref}/`);
}
