-- ============================================================================
-- Automation Workflow Intake System - Database Schema
-- ============================================================================
-- This schema supports the complete lifecycle of workflow automation intake,
-- routing, implementation, and monitoring.
--
-- Usage:
--   psql -U your_user -d automation_db < intake_database_schema.sql
-- ============================================================================

-- Create schema for intake system
CREATE SCHEMA IF NOT EXISTS intake;

-- ============================================================================
-- 1. WORKFLOW SUBMISSIONS TABLE
-- ============================================================================
-- Stores all submitted workflow automation requests

CREATE TABLE IF NOT EXISTS intake.workflow_submissions (
    -- Identity
    id SERIAL PRIMARY KEY,
    submission_id VARCHAR(50) UNIQUE NOT NULL,  -- e.g., WF-2024-001

    -- Metadata
    submission_date TIMESTAMP NOT NULL DEFAULT NOW(),
    submitted_by VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,  -- Marketing, Sales, BDR, CS, Finance, etc.
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('High', 'Medium', 'Low')),
    status VARCHAR(50) NOT NULL DEFAULT 'Submitted' CHECK (status IN (
        'Submitted',
        'Under Review',
        'Approved',
        'Rejected',
        'In Development',
        'Testing',
        'Deployed',
        'Paused',
        'Archived'
    )),

    -- Section 1: Problem Statement
    problem_statement TEXT NOT NULL,

    -- Section 2: Current Manual Process
    current_process JSONB NOT NULL,  -- Array of steps with time/frequency
    time_per_occurrence_minutes INTEGER,
    frequency_per_period INTEGER,
    frequency_period VARCHAR(20),  -- 'day', 'week', 'month'
    people_affected INTEGER,
    total_weekly_hours DECIMAL(10,2),

    -- Section 3: Desired Automation
    trigger_description TEXT,
    data_sources JSONB,  -- Array of {source, description, api_details}
    process_steps JSONB,  -- Array of automation steps
    outputs JSONB,  -- Array of {system, field, format, description}

    -- Section 4: Success Criteria
    success_criteria JSONB,  -- Array of {metric, before, after, measurement_method}

    -- Section 5: Constraints & Requirements
    integrations_required JSONB,  -- Array of {system, api, rate_limits, auth}
    cost_constraints JSONB,  -- {max_per_execution, max_monthly, details}
    volume_scale JSONB,  -- {average, peak, concurrent, response_time}
    compliance_requirements JSONB,  -- Array of compliance needs
    security_requirements JSONB,  -- Array of security needs
    human_approval_gates JSONB,  -- Array of approval gate descriptions
    other_requirements TEXT,

    -- Section 6: Complexity Signals
    decision_complexity JSONB,  -- {flags: [], explanation}
    integration_complexity JSONB,  -- {flags: [], explanation}
    state_management_complexity JSONB,  -- {flags: [], explanation}
    suggested_tier INTEGER CHECK (suggested_tier >= 0 AND suggested_tier <= 6),
    suggested_tier_reasoning TEXT,

    -- Section 7: Additional Context
    current_workarounds TEXT,
    related_workflows TEXT,
    known_edge_cases TEXT,
    dependencies TEXT,
    nice_to_haves TEXT,

    -- Routing & Assignment
    assigned_tier INTEGER CHECK (assigned_tier >= 0 AND assigned_tier <= 6),
    tier_assignment_date TIMESTAMP,
    tier_assignment_method VARCHAR(50),  -- 'Automated', 'Manual', 'Hybrid'
    tier_assignment_confidence DECIMAL(3,2),  -- 0.00 to 1.00
    assigned_to VARCHAR(255),  -- Implementation team member

    -- ROI Calculations
    estimated_weekly_hours_saved DECIMAL(10,2),
    estimated_annual_cost_savings DECIMAL(12,2),
    estimated_build_hours DECIMAL(10,2),
    estimated_build_cost DECIMAL(12,2),
    roi_score DECIMAL(10,2),  -- (Savings / Build Cost)

    -- Implementation Tracking
    implementation_start_date TIMESTAMP,
    estimated_completion_date TIMESTAMP,
    actual_completion_date TIMESTAMP,
    implementation_notes TEXT,

    -- Approval Workflow
    reviewer VARCHAR(255),
    review_date TIMESTAMP,
    review_notes TEXT,
    approval_date TIMESTAMP,
    approved_by VARCHAR(255),
    rejection_reason TEXT,

    -- Audit
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_by VARCHAR(255)
);

-- Indexes for common queries
CREATE INDEX idx_submissions_status ON intake.workflow_submissions(status);
CREATE INDEX idx_submissions_department ON intake.workflow_submissions(department);
CREATE INDEX idx_submissions_assigned_tier ON intake.workflow_submissions(assigned_tier);
CREATE INDEX idx_submissions_priority ON intake.workflow_submissions(priority);
CREATE INDEX idx_submissions_submission_date ON intake.workflow_submissions(submission_date DESC);
CREATE INDEX idx_submissions_roi_score ON intake.workflow_submissions(roi_score DESC NULLS LAST);

-- Full-text search on problem statements
CREATE INDEX idx_submissions_problem_fulltext ON intake.workflow_submissions
    USING gin(to_tsvector('english', problem_statement));

-- ============================================================================
-- 2. TIER ROUTING DECISIONS TABLE
-- ============================================================================
-- Logs all routing decisions (automated and manual) for analysis

CREATE TABLE IF NOT EXISTS intake.tier_routing_log (
    id SERIAL PRIMARY KEY,
    submission_id VARCHAR(50) REFERENCES intake.workflow_submissions(submission_id),

    -- Decision Details
    decision_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    decision_method VARCHAR(50) NOT NULL,  -- 'Automated', 'Manual Override', 'Hybrid'
    decided_by VARCHAR(255),  -- AI agent name or human user

    -- Complexity Analysis
    decision_complexity_score DECIMAL(3,2),  -- 0.00 to 1.00
    integration_complexity_score DECIMAL(3,2),
    state_complexity_score DECIMAL(3,2),
    overall_complexity_score DECIMAL(3,2),

    -- Tier Assignment
    recommended_tier INTEGER NOT NULL CHECK (recommended_tier >= 0 AND recommended_tier <= 6),
    confidence DECIMAL(3,2),  -- 0.00 to 1.00
    reasoning TEXT NOT NULL,

    -- Alternative Tiers Considered
    alternative_tiers JSONB,  -- Array of {tier, confidence, reasoning}

    -- Human Override (if applicable)
    was_overridden BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    original_tier INTEGER,
    final_tier INTEGER,

    -- Model/Agent Details (for automated decisions)
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    prompt_version VARCHAR(50),

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_routing_log_submission ON intake.tier_routing_log(submission_id);
CREATE INDEX idx_routing_log_method ON intake.tier_routing_log(decision_method);

-- ============================================================================
-- 3. WORKFLOW EXECUTIONS TABLE
-- ============================================================================
-- Tracks individual executions of deployed workflows

CREATE TABLE IF NOT EXISTS intake.workflow_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    submission_id VARCHAR(50) REFERENCES intake.workflow_submissions(submission_id),

    -- Execution Details
    start_time TIMESTAMP NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(50) NOT NULL CHECK (status IN (
        'Running',
        'Completed',
        'Failed',
        'Timeout',
        'Cancelled'
    )),

    -- Tier Execution Details
    tier INTEGER NOT NULL,
    execution_platform VARCHAR(100),  -- 'n8n', 'LangChain', 'LangGraph', etc.
    workflow_id VARCHAR(255),  -- Platform-specific workflow ID

    -- Input/Output
    input_data JSONB,
    output_data JSONB,

    -- Performance Metrics
    api_calls_made INTEGER DEFAULT 0,
    total_cost DECIMAL(10,4) DEFAULT 0.00,
    tokens_used INTEGER DEFAULT 0,

    -- Error Handling
    error_message TEXT,
    error_stack TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Metadata
    triggered_by VARCHAR(255),
    environment VARCHAR(50),  -- 'production', 'staging', 'development'

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_executions_submission ON intake.workflow_executions(submission_id);
CREATE INDEX idx_executions_status ON intake.workflow_executions(status);
CREATE INDEX idx_executions_start_time ON intake.workflow_executions(start_time DESC);
CREATE INDEX idx_executions_tier ON intake.workflow_executions(tier);

-- ============================================================================
-- 4. SUCCESS METRICS TABLE
-- ============================================================================
-- Tracks actual vs. expected success criteria for deployed workflows

CREATE TABLE IF NOT EXISTS intake.success_metrics (
    id SERIAL PRIMARY KEY,
    submission_id VARCHAR(50) REFERENCES intake.workflow_submissions(submission_id),

    -- Metric Details
    metric_name VARCHAR(255) NOT NULL,
    metric_type VARCHAR(50),  -- 'Time Savings', 'Capacity', 'Speed', 'Quality', 'Cost'

    -- Expected Values (from success criteria)
    expected_before_value DECIMAL(12,2),
    expected_after_value DECIMAL(12,2),
    expected_unit VARCHAR(50),  -- 'minutes', 'hours', 'count', 'score', 'dollars'

    -- Actual Measured Values
    actual_before_value DECIMAL(12,2),
    actual_after_value DECIMAL(12,2),
    actual_improvement_pct DECIMAL(5,2),

    -- Measurement Details
    measurement_start_date DATE,
    measurement_end_date DATE,
    measurement_period_days INTEGER,
    sample_size INTEGER,
    measurement_method TEXT,

    -- Validation
    target_met BOOLEAN,
    variance_pct DECIMAL(5,2),  -- (Actual - Expected) / Expected
    notes TEXT,

    -- Metadata
    measured_by VARCHAR(255),
    measured_at TIMESTAMP NOT NULL DEFAULT NOW(),

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_success_metrics_submission ON intake.success_metrics(submission_id);
CREATE INDEX idx_success_metrics_type ON intake.success_metrics(metric_type);
CREATE INDEX idx_success_metrics_target_met ON intake.success_metrics(target_met);

-- ============================================================================
-- 5. FEEDBACK & ITERATIONS TABLE
-- ============================================================================
-- Captures user feedback and improvement iterations

CREATE TABLE IF NOT EXISTS intake.workflow_feedback (
    id SERIAL PRIMARY KEY,
    submission_id VARCHAR(50) REFERENCES intake.workflow_submissions(submission_id),
    execution_id VARCHAR(100) REFERENCES intake.workflow_executions(execution_id),

    -- Feedback Details
    feedback_date TIMESTAMP NOT NULL DEFAULT NOW(),
    feedback_by VARCHAR(255) NOT NULL,

    -- Ratings
    usefulness_score INTEGER CHECK (usefulness_score >= 1 AND usefulness_score <= 5),
    quality_score INTEGER CHECK (quality_score >= 1 AND quality_score <= 5),
    speed_score INTEGER CHECK (speed_score >= 1 AND speed_score <= 5),

    -- Qualitative Feedback
    what_worked_well TEXT,
    what_needs_improvement TEXT,
    edge_cases_found TEXT,
    feature_requests TEXT,

    -- Issue Tracking
    is_bug_report BOOLEAN DEFAULT FALSE,
    bug_severity VARCHAR(20),  -- 'Low', 'Medium', 'High', 'Critical'
    bug_description TEXT,

    -- Follow-up
    requires_iteration BOOLEAN DEFAULT FALSE,
    iteration_priority VARCHAR(20),  -- 'High', 'Medium', 'Low'
    iteration_implemented BOOLEAN DEFAULT FALSE,
    iteration_date TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_submission ON intake.workflow_feedback(submission_id);
CREATE INDEX idx_feedback_requires_iteration ON intake.workflow_feedback(requires_iteration);
CREATE INDEX idx_feedback_bug_report ON intake.workflow_feedback(is_bug_report);

-- ============================================================================
-- 6. VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Pending Submissions Needing Review
CREATE OR REPLACE VIEW intake.pending_review AS
SELECT
    submission_id,
    submitted_by,
    department,
    priority,
    problem_statement,
    submission_date,
    total_weekly_hours,
    suggested_tier
FROM intake.workflow_submissions
WHERE status = 'Submitted'
ORDER BY
    CASE priority
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END,
    total_weekly_hours DESC NULLS LAST,
    submission_date ASC;

-- View: ROI Ranking (Top Automation Candidates)
CREATE OR REPLACE VIEW intake.roi_ranking AS
SELECT
    submission_id,
    department,
    problem_statement,
    total_weekly_hours,
    estimated_annual_cost_savings,
    estimated_build_cost,
    roi_score,
    assigned_tier,
    status
FROM intake.workflow_submissions
WHERE status IN ('Submitted', 'Approved', 'Under Review')
    AND roi_score IS NOT NULL
ORDER BY roi_score DESC;

-- View: Workflow Performance Dashboard
CREATE OR REPLACE VIEW intake.workflow_performance AS
SELECT
    ws.submission_id,
    ws.department,
    ws.assigned_tier,
    ws.status,
    COUNT(we.id) as total_executions,
    AVG(we.duration_seconds) as avg_duration_seconds,
    SUM(we.total_cost) as total_cost,
    SUM(CASE WHEN we.status = 'Completed' THEN 1 ELSE 0 END) as successful_executions,
    SUM(CASE WHEN we.status = 'Failed' THEN 1 ELSE 0 END) as failed_executions,
    AVG(wf.usefulness_score) as avg_usefulness_score,
    AVG(wf.quality_score) as avg_quality_score
FROM intake.workflow_submissions ws
LEFT JOIN intake.workflow_executions we ON ws.submission_id = we.submission_id
LEFT JOIN intake.workflow_feedback wf ON ws.submission_id = wf.submission_id
WHERE ws.status = 'Deployed'
GROUP BY ws.submission_id, ws.department, ws.assigned_tier, ws.status;

-- View: Tier Routing Accuracy
CREATE OR REPLACE VIEW intake.tier_routing_accuracy AS
SELECT
    tr.recommended_tier,
    tr.decision_method,
    COUNT(*) as total_assignments,
    AVG(tr.confidence) as avg_confidence,
    SUM(CASE WHEN tr.was_overridden THEN 1 ELSE 0 END) as override_count,
    AVG(sm.actual_improvement_pct) as avg_improvement_achieved
FROM intake.tier_routing_log tr
JOIN intake.workflow_submissions ws ON tr.submission_id = ws.submission_id
LEFT JOIN intake.success_metrics sm ON ws.submission_id = sm.submission_id
GROUP BY tr.recommended_tier, tr.decision_method
ORDER BY tr.recommended_tier;

-- ============================================================================
-- 7. HELPER FUNCTIONS
-- ============================================================================

-- Function: Generate next submission ID
CREATE OR REPLACE FUNCTION intake.generate_submission_id()
RETURNS VARCHAR(50) AS $$
DECLARE
    next_id INTEGER;
    year VARCHAR(4);
    new_submission_id VARCHAR(50);
BEGIN
    year := TO_CHAR(CURRENT_DATE, 'YYYY');

    SELECT COALESCE(MAX(CAST(SUBSTRING(submission_id FROM 9) AS INTEGER)), 0) + 1
    INTO next_id
    FROM intake.workflow_submissions
    WHERE submission_id LIKE 'WF-' || year || '-%';

    new_submission_id := 'WF-' || year || '-' || LPAD(next_id::TEXT, 3, '0');

    RETURN new_submission_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Calculate ROI score
CREATE OR REPLACE FUNCTION intake.calculate_roi_score(
    p_submission_id VARCHAR(50)
) RETURNS DECIMAL(10,2) AS $$
DECLARE
    v_annual_savings DECIMAL(12,2);
    v_build_cost DECIMAL(12,2);
    v_roi DECIMAL(10,2);
BEGIN
    SELECT
        estimated_annual_cost_savings,
        estimated_build_cost
    INTO v_annual_savings, v_build_cost
    FROM intake.workflow_submissions
    WHERE submission_id = p_submission_id;

    IF v_build_cost IS NULL OR v_build_cost = 0 THEN
        RETURN NULL;
    END IF;

    v_roi := v_annual_savings / v_build_cost;

    RETURN v_roi;
END;
$$ LANGUAGE plpgsql;

-- Function: Update timestamp trigger
CREATE OR REPLACE FUNCTION intake.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to workflow_submissions
CREATE TRIGGER trigger_update_workflow_submissions
    BEFORE UPDATE ON intake.workflow_submissions
    FOR EACH ROW
    EXECUTE FUNCTION intake.update_updated_at();

-- ============================================================================
-- 8. SAMPLE DATA (for testing)
-- ============================================================================

-- Uncomment to insert sample submission
/*
INSERT INTO intake.workflow_submissions (
    submission_id,
    submitted_by,
    department,
    priority,
    problem_statement,
    current_process,
    time_per_occurrence_minutes,
    frequency_per_period,
    frequency_period,
    people_affected,
    total_weekly_hours,
    suggested_tier,
    suggested_tier_reasoning
) VALUES (
    intake.generate_submission_id(),
    'john.doe@company.com',
    'BDR',
    'High',
    'BDRs waste 10-15 min/lead manually researching companies before outreach, reducing capacity from 20 to 12 qualified conversations per day.',
    '[{"step": 1, "description": "Receive Slack notification", "tool": "Slack"}, {"step": 2, "description": "Open Salesforce and copy company name", "tool": "Salesforce"}]'::JSONB,
    12,
    25,
    'day',
    8,
    80.0,
    2,
    'Tier 2-3: Requires Claude API for synthesis and NLG, orchestrates multiple APIs (Marketo, Salesforce, ZoomInfo), but single-pass execution with no complex state management.'
);
*/

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
