# :fish_cake: lumina

Experimental API service for New Theatre alumni sites, responsible for identifying members and processing messages and submissions of data.

# Data Model

Data is stored in DynamoDB in a single table, `LuminaMember`. It stores member information and submissions by those members.

| Partition Key    | Sort Key          | Data                 |
| ---------------- | ----------------- | -------------------- |
| `<Member ID>`    | `profile`         | Member profile       |
| `<Member ID>`    | `<Submission ID>` | Member submission    |
| `<Anonymous ID>` | `<Submission ID>` | Anonymous submission |

## MemberModel

Stores information about a member when they register for the Alumni Network.

### Member Consent

We track member consent for a number of scenarios. We only collect and process data for internal purposes and do not share it with third parties.
When a member consents to a specific use of their data we store the date of consent in the `MemberConsent` model.

| Scenario           | Description                                                                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `consent_news`     | We can contact the member about news and events for the Alumni Network.                                                                         |
| `consent_network`  | We can contact the member                                                                                                                       |
| `consent_members`  | Other members of the alumni network can get in touch. We do not share details with other members but allow the 'first email' to be sent via us. |
| `consent_students` | Current students can get in touch. We do not share details with other members but allow the 'first email' to be sent via us.                    |

## SubmissionModel

Stores submissions both from registered members and anonymous users. When a user is anonymous we store their name and optionally grad year and email in the `submitter` field.
