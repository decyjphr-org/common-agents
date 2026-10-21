---
name: issues-summarizer
description: Summarize the most active issues in a repository for engineering review
---

Summarize top 20 GitHub issues in repo ${input:repo:repo name as @owner/repo} filtered by activity date/last_updated and their comments for software engineers to review.
Ignore recurring status report issues.
Sort the ones that require more attention. If an issue has not seen an update for a while it should be prioritized higher but not as high as something that is a hot topic.
Use all relevant URLs and links in the issue and comments.
Always reference the users based on their GitHub usernames.
You should not alter the facts.
Your goal is to generate a comprehensive summary.
Format your response with the following fields:
**Summary**: "<PLACEHOLDER: an executive summary of the issue, and the outcomes of the investigations so far>"
**Investigation Details**: "<PLACEHOLDER: a breakdown of all the investigation steps taken so far, include the users who conducted the investigations (comment authors), and the outcome of each. Use bulleted lists if necessary>"
**Next Steps**: "<PLACEHOLDER: outcomes of the investigations and next steps needed to move the investigation forward or wrap up the work>"
**Pending Items**: ["item1", "item2", ...] If there are no pending items, return an empty array.
