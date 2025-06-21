# 🔒 Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

The Kensho team and community take security bugs seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

### Where to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them by email to: **[Your Email Here]**

### What to Include

Please include the following information along with your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### Response Timeline

- **Initial Response**: We'll acknowledge your email within 48 hours
- **Status Update**: We'll send a more detailed response within 5 days indicating the next steps
- **Resolution**: We aim to resolve critical issues within 30 days

### What to Expect

After you submit a report, we'll:

1. **Confirm the problem** and determine the affected versions
2. **Audit code** to find any potential similar problems
3. **Prepare fixes** for all releases still under support
4. **Release fixed versions** as soon as possible
5. **Announce the vulnerability** after fixes are released

## Security Considerations

### API Keys

- **Never commit API keys** to version control
- **Use environment variables** for sensitive configuration
- **Rotate keys regularly** and revoke unused keys
- **Use least privilege principle** for API access

### File Uploads

- **Validate file types** before processing
- **Scan uploaded content** for malicious files
- **Limit file sizes** to prevent DoS attacks
- **Store uploads securely** with proper access controls

### Data Privacy

- **Encrypt sensitive data** at rest and in transit
- **Implement proper authentication** and authorization
- **Log security events** but not sensitive data
- **Follow data retention policies** and delete old data

### Dependencies

- **Keep dependencies updated** to latest secure versions
- **Monitor for security advisories** using tools like GitHub Security Alerts
- **Review third-party packages** before adding to the project
- **Use dependency scanning** in CI/CD pipelines

### Docker Security

- **Use non-root users** in containers
- **Keep base images updated** with security patches
- **Scan container images** for vulnerabilities
- **Limit container permissions** and capabilities

## Security Features

### Current Implementations

- **HTTPS enforcement** in production environments
- **Input validation** for all user inputs
- **File type restrictions** for uploads
- **Rate limiting** on API endpoints
- **Session management** with secure cookies
- **CORS configuration** for cross-origin requests

### Planned Improvements

- **CSP headers** for XSS protection
- **Authentication system** for user management
- **Audit logging** for security events
- **Automated security scanning** in CI/CD
- **Regular security assessments**

## Compliance

This project aims to follow security best practices including:

- **OWASP Top 10** web application security risks
- **NIST Cybersecurity Framework** guidelines
- **Secure coding practices** for Python and JavaScript
- **Container security** best practices

## Community

Security is everyone's responsibility. We encourage:

- **Code reviews** for all changes
- **Security testing** as part of development
- **Reporting suspicious behavior** or potential vulnerabilities
- **Following secure coding practices** in contributions

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.org/dev/security/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

---

Thank you for helping keep Kensho and our users safe! 🛡️ 