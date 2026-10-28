// Run with: node --test web/
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { allocate, intToIp, ipToInt, parseCidr, prefixForHosts } from "./vlsm.js";

const ANIMAL_KINGDOM = [
  { name: "dog-lan", hosts: 1200 },
  { name: "cat-lan", hosts: 800 },
  { name: "elephant-lan", hosts: 100 },
  { name: "lion-lan", hosts: 10 },
  { name: "lion-elephant", hosts: 2 },
  { name: "elephant-cat", hosts: 2 },
  { name: "elephant-dog", hosts: 2 },
];

test("matches the Python planner's committed output (docs/generated/plan.json)", () => {
  const python = JSON.parse(readFileSync(new URL("../docs/generated/plan.json", import.meta.url)));
  const js = allocate("10.0.0.0/8", ANIMAL_KINGDOM);
  assert.deepEqual(
    js.map((a) => [a.name, a.network, a.netmask, a.wildcard, a.firstHost, a.lastHost, a.broadcast]),
    python.map((a) => [a.name, a.network, a.netmask, a.wildcard, a.first_host, a.last_host, a.broadcast]),
  );
});

test("prefixForHosts boundaries", () => {
  for (const [hosts, prefix] of [[1, 30], [2, 30], [3, 29], [14, 28], [15, 27], [1022, 22], [1023, 21]]) {
    assert.equal(prefixForHosts(hosts), prefix, `hosts=${hosts}`);
  }
  assert.throws(() => prefixForHosts(0), /hosts must be/);
});

test("ip conversions round-trip", () => {
  for (const ip of ["0.0.0.0", "10.0.12.145", "255.255.255.255"]) assert.equal(intToIp(ipToInt(ip)), ip);
  assert.throws(() => ipToInt("10.0.0.256"), /invalid/);
  assert.throws(() => ipToInt("10.0.0"), /invalid/);
});

test("rejects bad input", () => {
  assert.throws(() => parseCidr("10.0.0.1/24"), /host bits/);
  assert.throws(() => parseCidr("10.0.0.0/33"), /prefix/);
  assert.throws(() => allocate("192.168.1.0/24", [{ name: "a", hosts: 300 }]), /larger than/);
  assert.throws(() => allocate("192.168.1.0/30", [{ name: "a", hosts: 2 }, { name: "b", hosts: 2 }]), /no room/);
  assert.throws(() => allocate("10.0.0.0/8", [{ name: "a", hosts: 2 }, { name: "a", hosts: 2 }]), /duplicate/);
});

test("random plans never overlap and stay aligned", () => {
  let seed = 42;
  const rand = () => (seed = (seed * 1103515245 + 12345) % 2 ** 31) / 2 ** 31;
  for (let i = 0; i < 500; i++) {
    const reqs = Array.from({ length: 1 + Math.floor(rand() * 20) }, (_, j) => ({
      name: `n${j}`,
      hosts: 1 + Math.floor(rand() * 4000),
    }));
    const plan = allocate("10.0.0.0/8", reqs).sort((a, b) => a.start - b.start);
    plan.forEach((a, j) => {
      assert.equal(a.start % a.size, 0);
      assert.ok(a.usableHosts >= a.hostsRequired);
      if (j > 0) assert.ok(plan[j - 1].start + plan[j - 1].size <= a.start);
    });
  }
});
