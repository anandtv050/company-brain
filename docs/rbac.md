# RBAC design (HRMS slice)

**Rule zero: the LLM never decides permissions.** The HRMS API checks every call against
`services/hrms-api/policy.yaml`; MCP passes the user's token through; RAG filters by role
before searching. A prompt saying "don't reveal salaries" is not security.

Permission = **role × scope × sensitivity**.

## Roles

| Role | Who | Widest scope |
| --- | --- | --- |
| `employee` | Every active employee | self + directory |
| `manager` | Anyone with reportees (derived from `manager_id`) | team (direct + indirect) |
| `hr_exec` | HR Executive, Recruiter | all, no salary |
| `hr_payroll` | Payroll Specialist, HR Head | all incl. salary |
| `finance` | Finance team | aggregates only |
| `it_admin` | IT Helpdesk | assets |
| `leadership` | CEO, CXOs | all |
| `ai_service` | Scheduled / event jobs | limited; in chat the agent always acts as the user |

A user holds several roles (a Tech Lead is `employee` + `manager`); the widest scope wins.

## Sensitivity

| Level | Examples |
| --- | --- |
| Public-internal | Policies, holidays, org chart, directory basics |
| Internal | Phone, attendance, leave history, onboarding |
| Confidential | Performance ratings, reviews, manager handbook |
| Restricted | Salary, payslips, medical leave reasons, disciplinary |

## Permission matrix

`—` = denied. `aggregate` = counts and sums only, never one person's row.

| Resource · action | employee | manager | hr_exec | hr_payroll | finance | leadership |
| --- | --- | --- | --- | --- | --- | --- |
| Directory · read | all (limited fields) | all | all | all | all | all |
| Profile · read | self | team | all | all | — | all |
| Leave · read | self | team | all | all | — | all |
| Leave · apply | self | self | self | self | self | self |
| Leave · approve | — | team | all | — | — | — |
| Medical leave reason · read | self | — | all | all | — | — |
| Attendance · read | self | team | all | all | — | aggregate |
| Salary · read | self | — | — | all | aggregate | all |
| Payslip · read | self | — | — | all | — | — |
| Performance · read | self | team | all | all | — | all |
| Headcount stats | — | team | all | all | all | all |

## Hard rules

1. A manager loses scope over an employee the moment `manager_id` changes.
2. Exited employees are visible to `hr_exec`, `hr_payroll` and `leadership` only.
3. Nobody approves their own leave. If the manager is on leave, approval goes one level up.
4. `ai_service` writes only create approval requests; a human decision executes them.
5. Every allow and deny goes to `audit_log` with acting user and `on_behalf_of`.

## Demo personas

Fixed in the seed so evals stay stable.

| Persona | Designation | Roles | Tests |
| --- | --- | --- | --- |
| Priya | HR Head | employee, hr_exec, hr_payroll | Full HR access, salary |
| Arjun | Engineering Manager (12 reportees) | employee, manager | Team scope |
| Meera | SSE, reports to Arjun | employee | Self only |
| Rahul | Intern, on probation | employee | Least access, probation flows |
| Fathima | Finance Manager | employee, finance | Aggregates, no personal salary |
| Vikram | CEO | employee, leadership | Everything |

## First permission tests (written on Day 4)

| Persona | Asks for | Expected |
| --- | --- | --- |
| Meera | Arjun's salary | deny |
| Meera | Her own payslip | allow |
| Arjun | Meera's performance rating | allow (team) |
| Arjun | Priya's leave history | deny |
| Rahul | Average engineering salary | deny |
| Fathima | Total payroll by department | allow (aggregate) |
| Fathima | Meera's salary | deny |
| Priya | Any payslip | allow |
| Arjun | Approve his own leave | deny |
| Old manager | Ex-reportee's leave after transfer | deny |
