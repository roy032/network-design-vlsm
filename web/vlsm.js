// VLSM allocation in the browser. Mirrors src/vlsmkit/allocator.py exactly;
// web/vlsm.test.mjs checks both produce the same plan.

/** @param {string} ip */
export function ipToInt(ip) {
  const parts = ip.trim().split(".");
  if (parts.length !== 4) throw new Error(`invalid IPv4 address: ${ip}`);
  return parts.reduce((acc, part) => {
    if (!/^\d{1,3}$/.test(part) || Number(part) > 255) {
      throw new Error(`invalid IPv4 address: ${ip}`);
    }
    return acc * 256 + Number(part);
  }, 0);
}

/** @param {number} n */
export function intToIp(n) {
  return [24, 16, 8, 0].map((s) => Math.floor(n / 2 ** s) % 256).join(".");
}

/** @param {string} cidr */
export function parseCidr(cidr) {
  const [ip, len] = cidr.trim().split("/");
  const prefix = Number(len);
  if (!Number.isInteger(prefix) || prefix < 0 || prefix > 32) {
    throw new Error(`invalid prefix length in ${cidr}`);
  }
  const size = 2 ** (32 - prefix);
  const address = ipToInt(ip);
  if (address % size !== 0) {
    throw new Error(`${cidr} has host bits set (did you mean ${intToIp(address - (address % size))}/${prefix}?)`);
  }
  return { start: address, prefix, size };
}

export const usableHosts = (prefix) => Math.max(2 ** (32 - prefix) - 2, 0);

export const maskOf = (prefix) => intToIp(2 ** 32 - 2 ** (32 - prefix));

export const wildcardOf = (prefix) => intToIp(2 ** (32 - prefix) - 1);

/** Smallest subnet (longest prefix) with at least `hosts` usable addresses. */
export function prefixForHosts(hosts) {
  if (!Number.isInteger(hosts) || hosts < 1) throw new Error(`hosts must be >= 1, got ${hosts}`);
  let bits = 2;
  while (2 ** bits < hosts + 2) bits += 1;
  if (bits > 32) throw new Error(`${hosts} hosts cannot fit in an IPv4 subnet`);
  return 32 - bits;
}

/**
 * Allocate largest-first, aligned, from the start of the parent block.
 * @param {string} parentCidr
 * @param {{name: string, hosts: number}[]} requests
 */
export function allocate(parentCidr, requests) {
  const parent = parseCidr(parentCidr);
  const seen = new Set();
  for (const r of requests) {
    if (!r.name) throw new Error("every subnet needs a name");
    if (seen.has(r.name)) throw new Error(`duplicate subnet name: ${r.name}`);
    seen.add(r.name);
  }
  // Array.prototype.sort is stable, so equal sizes keep their input order.
  const ordered = requests
    .map((r) => ({ ...r, prefix: prefixForHosts(r.hosts) }))
    .sort((a, b) => a.prefix - b.prefix);

  let cursor = parent.start;
  const end = parent.start + parent.size;
  return ordered.map((r) => {
    if (r.prefix < parent.prefix) throw new Error(`${r.name} needs a /${r.prefix}, larger than ${parentCidr}`);
    const size = 2 ** (32 - r.prefix);
    const start = Math.ceil(cursor / size) * size;
    if (start + size > end) {
      throw new Error(`${parentCidr} has no room left for ${r.name} (${r.hosts} hosts, /${r.prefix})`);
    }
    cursor = start + size;
    return {
      name: r.name,
      hostsRequired: r.hosts,
      usableHosts: usableHosts(r.prefix),
      prefix: r.prefix,
      start,
      size,
      network: `${intToIp(start)}/${r.prefix}`,
      netmask: maskOf(r.prefix),
      wildcard: wildcardOf(r.prefix),
      firstHost: intToIp(start + 1),
      lastHost: intToIp(start + size - 2),
      broadcast: intToIp(start + size - 1),
    };
  });
}
