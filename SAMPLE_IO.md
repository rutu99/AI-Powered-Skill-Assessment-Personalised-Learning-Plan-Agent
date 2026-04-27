# Sample Inputs & Outputs

## Example 1: Data Analyst Assessment

### Input: Job Description
```
Position: Senior Data Analyst

We need a data-driven analyst who can handle complex queries and tell stories with data.

Required Skills:
- SQL (window functions, CTEs, query optimisation)
- Python (Pandas, NumPy, Matplotlib)
- Tableau or Power BI
- Statistical analysis (hypothesis testing, regression)
- A/B testing design and analysis
- BigQuery or Redshift experience
- Strong communication and stakeholder management
```

### Input: Resume (Text)
```
Sayali Kamble
Data Analyst | priya@example.com | LinkedIn: /in/priyasharma

EXPERIENCE
Data Analyst, FinTech Startup (2022–Present)
- Built customer churn prediction model using Python (Pandas, scikit-learn)
- Wrote complex SQL queries for revenue reporting across PostgreSQL databases
- Created Power BI dashboards for C-suite weekly reporting
- Collaborated with marketing on campaign analysis

SKILLS
Languages: Python (Pandas, NumPy, Matplotlib), SQL, R (basic)
Tools: Power BI, Excel, Jupyter, Git
Databases: PostgreSQL, MySQL
Cloud: Some AWS experience

EDUCATION
B.Sc. Statistics — University of Delhi (2022)
```

### Assessment Conversation (Sample)
```
Agent: Hi Sayali! I'll be assessing 7 skills: SQL, Python, Tableau/Power BI, 
Statistical Analysis, A/B Testing, BigQuery, Communication.
Let's start with SQL.

Q1: Describe the most complex SQL query you've written. What business problem 
    did it solve and what techniques did you use?

Sayali: I wrote a revenue attribution query joining 5 tables — transactions, 
       users, campaigns, products, and regions. Used multiple CTEs to stage 
       intermediate aggregations, then a final query with CASE WHEN for 
       revenue bucketing. It ran on 10M rows and I had to add composite 
       indexes to get it under 3 seconds.

Q2: When would you use a window function instead of GROUP BY? 
    Give a specific example.

Sayali: Window functions when I need row-level context alongside aggregates. 
       For example, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY date) 
       to identify each user's first purchase — GROUP BY would collapse the 
       rows and I'd lose that detail.

Q3: Your query on a 50M row table suddenly got slow after a schema migration. 
    Walk me through your debugging process.

Sayali: First I'd run EXPLAIN ANALYZE to see the query plan. Check if there's 
       a sequential scan where I expect an index scan — migration might have 
       dropped indexes. Then check if statistics are stale (ANALYZE table). 
       Also check if any new columns need indexes or if data distribution 
       changed significantly.

[SQL Score: 8/10 — "Strong CTEs and window function understanding; good 
debugging methodology with EXPLAIN ANALYZE"]

---

Q1 (A/B Testing): How would you design an A/B test to measure whether a 
new checkout button colour increases conversions?

Sayali: I'd split traffic 50/50, run it for at least 2 weeks to account for 
       weekly patterns. Track conversion rate as primary metric. 
       Probably use a chi-square test... I think.

Q2 (A/B Testing): What sample size would you need and how do you determine 
when to stop the test?

Sayali: Honestly, I usually just look at whether the results seem significant 
       after a few days... I know there's a formula but I'd need to look it up.

[A/B Testing Score: 4/10 — "Understands basic concept but lacks statistical 
rigour; no mention of power analysis, p-values, or stopping rules"]
```

### Output: Report
```json
{
  "candidate_name": "Sayali Kamble",
  "target_role": "Senior Data Analyst",
  "date": "2024-01-15",
  "overall_score": 6.1,
  "skill_scores": {
    "SQL": {"score": 8, "evidence": "Strong CTEs, window functions, query optimisation knowledge"},
    "Python": {"score": 7, "evidence": "Practical Pandas/NumPy usage; solid for the role"},
    "Power BI": {"score": 7, "evidence": "Production BI experience though Tableau-specific knowledge missing"},
    "Statistical Analysis": {"score": 6, "evidence": "Good intuition but gaps in formal testing frameworks"},
    "A/B Testing": {"score": 4, "evidence": "Surface understanding; lacks power analysis and statistical rigour"},
    "BigQuery": {"score": 3, "evidence": "No direct experience; SQL skills transfer but syntax gaps expected"},
    "Communication": {"score": 8, "evidence": "Clear explanations, good at framing technical answers in context"}
  },
  "gaps": [
    "A/B Testing (4/10): Lacks statistical rigour, power analysis, p-value interpretation",
    "BigQuery (3/10): No direct experience with Google Cloud data warehouse syntax",
    "Statistical Analysis (6/10): Solid intuition but needs formal hypothesis testing framework"
  ],
  "learning_plan": [
    {
      "skill": "A/B Testing & Statistical Significance",
      "priority": "high",
      "time_estimate": "2 weeks",
      "rationale": "Her statistics degree means she has the maths foundation — she just needs to connect theory to practice",
      "resources": [
        {
          "title": "Udacity: A/B Testing (Free Course)",
          "url": "https://www.udacity.com/course/ab-testing--ud257",
          "type": "Course",
          "duration": "8 hours"
        },
        {
          "title": "Evan's Awesome A/B Tools (Sample Size Calculator)",
          "url": "https://www.evanmiller.org/ab-testing/",
          "type": "Tool",
          "duration": "1 hour"
        },
        {
          "title": "Statistics for Data Science — Khan Academy",
          "url": "https://www.khanacademy.org/math/statistics-probability",
          "type": "Course",
          "duration": "5 hours (targeted modules)"
        }
      ]
    },
    {
      "skill": "Google BigQuery",
      "priority": "high",
      "time_estimate": "1 week",
      "rationale": "Her PostgreSQL expertise means the SQL transfers directly; she only needs BigQuery syntax, partitioning, and clustering concepts",
      "resources": [
        {
          "title": "BigQuery Quickstart — Google Cloud Skills Boost (Free)",
          "url": "https://www.cloudskillsboost.google/focuses/1654",
          "type": "Lab",
          "duration": "3 hours"
        },
        {
          "title": "BigQuery for Data Analysts — Google Documentation",
          "url": "https://cloud.google.com/bigquery/docs/introduction",
          "type": "Documentation",
          "duration": "4 hours"
        }
      ]
    }
  ],
  "recommendation": "Sayali is a strong candidate. Her SQL and Python skills are genuinely impressive and would take years to develop from scratch. The gaps in A/B testing rigour and BigQuery are both learnable in under 3 weeks given her statistical education and SQL foundation. Recommend a conditional offer with specific 30-day learning milestones: complete the Udacity A/B Testing course and BigQuery lab, with a follow-up technical discussion. Her communication skills and analytical thinking are standout."
}
```
