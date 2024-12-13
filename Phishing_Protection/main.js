const maliciousUrls = [
    "example-malicious.com",
    "phishing-site.net",
    "bad-site.org",
    "youtube.com"
];

console.log(`Checking URL: ${details.url}`);
console.log(`Hostname: ${url.hostname}`);

const url = new URL(details.url);
if (maliciousUrls.some(domain => url.hostname.toLowerCase() === domain.toLowerCase())) {
    console.log(`Blocked: ${url.hostname}`);
    // return { cancel: true };
}