# Skills in Claude Code

Skills are reusable, specialized capabilities that Claude Code can invoke to handle specific domains or complex operations. They enable modular, composable automation workflows by breaking complex problems into domain-specific skill sets.

## Advanced Example

**Concept:** Custom skill creation and orchestration for enterprise automation

```javascript
// Real scenario: Enterprise data governance and compliance system

class SkillOrchestrationPlatform {
  constructor() {
    this.skills = new Map();
    this.skillRegistry = new SkillRegistry();
  }

  async registerCustomSkills() {
    // Skill 1: Data Classification & PII Detection
    this.registerSkill('data_classifier', {
      description: 'Classify data and detect PII',
      capabilities: [
        'Identify sensitive data (PII, financial, health)',
        'Classify data sensitivity level (public, internal, confidential)',
        'Generate compliance reports'
      ],
      requiredContext: ['data_samples', 'classification_rules'],
      outputFormat: {
        classifications: [{
          dataElement: 'string',
          sensitivityLevel: 'enum[public|internal|confidential]',
          piiType: 'enum[name|email|phone|ssn|credit_card|health]',
          complianceFramework: 'enum[GDPR|CCPA|HIPAA|PCI-DSS]'
        }]
      }
    });

    // Skill 2: Access Control Management
    this.registerSkill('access_control', {
      description: 'Manage data access and permissions',
      capabilities: [
        'Define access policies',
        'Assign roles and permissions',
        'Audit access logs',
        'Implement least-privilege principle'
      ],
      requiredContext: ['user_roles', 'data_classification', 'policies'],
      outputFormat: {
        accessPolicy: {
          role: 'string',
          resource: 'string',
          permissions: 'string[]',
          conditions: 'object'
        }
      }
    });

    // Skill 3: Data Encryption & Security
    this.registerSkill('data_encryption', {
      description: 'Encrypt sensitive data and manage keys',
      capabilities: [
        'Encrypt data at rest',
        'Implement field-level encryption',
        'Manage encryption keys',
        'Generate security certificates'
      ],
      requiredContext: ['encryption_standards', 'key_management_policy'],
      outputFormat: {
        encrypted: true,
        algorithm: 'string',
        keyId: 'string'
      }
    });

    // Skill 4: Compliance Audit
    this.registerSkill('compliance_audit', {
      description: 'Audit compliance with regulations',
      capabilities: [
        'Check GDPR compliance',
        'Check CCPA compliance',
        'Verify data retention policies',
        'Generate audit reports'
      ],
      requiredContext: ['regulations', 'data_practices'],
      outputFormat: {
        framework: 'string',
        status: 'enum[compliant|non_compliant|warning]',
        findings: 'object[]'
      }
    });

    // Skill 5: Incident Response
    this.registerSkill('incident_response', {
      description: 'Respond to data breaches and compliance issues',
      capabilities: [
        'Detect data breaches',
        'Isolate compromised systems',
        'Notify affected parties',
        'Document incident timeline'
      ],
      requiredContext: ['incident_data', 'response_procedures'],
      outputFormat: {
        incidentId: 'string',
        severity: 'enum[low|medium|high|critical]',
        actions: 'object[]'
      }
    });
  }

  registerSkill(name, definition) {
    this.skills.set(name, definition);
    this.skillRegistry.register(definition);
  }

  async executeComplexWorkflow(request) {
    // Request: "Implement GDPR compliance for our customer database"

    const workflow = await this.createWorkflow(request);
    // Workflow includes:
    // 1. Data Classification → uses data_classifier skill
    // 2. Access Control Setup → uses access_control skill
    // 3. Data Encryption → uses data_encryption skill
    // 4. Compliance Audit → uses compliance_audit skill
    // 5. Documentation → generates compliance report

    const execution = {
      phase1: async () => {
        return await this.executeSkill('data_classifier', {
          target: 'customer_database',
          frameworks: ['GDPR', 'CCPA']
        });
      },

      phase2: async (classification) => {
        return await this.executeSkill('access_control', {
          classified_data: classification,
          principle: 'least_privilege'
        });
      },

      phase3: async (accessPolicy) => {
        return await this.executeSkill('data_encryption', {
          sensitive_data: accessPolicy.protectedResources,
          standard: 'AES-256'
        });
      },

      phase4: async (encryption) => {
        return await this.executeSkill('compliance_audit', {
          framework: 'GDPR',
          implementations: [encryption, accessPolicy]
        });
      },

      phase5: async (auditResult) => {
        if (auditResult.status === 'compliant') {
          return {
            status: 'compliant',
            certifications: ['GDPR', 'ISO27001'],
            report: await this.generateComplianceReport(auditResult)
          };
        } else if (auditResult.status === 'non_compliant') {
          return await this.executeSkill('incident_response', {
            incident_type: 'compliance_violation',
            findings: auditResult.findings
          });
        }
      }
    };

    // Execute phases sequentially with proper dependency handling
    let result = await execution.phase1();
    result = await execution.phase2(result);
    result = await execution.phase3(result);
    result = await execution.phase4(result);
    result = await execution.phase5(result);

    return result;
  }

  async executeSkill(skillName, params) {
    const skill = this.skills.get(skillName);

    if (!skill) {
      throw new Error(`Skill '${skillName}' not found`);
    }

    // Validate input parameters
    const validated = this.validateSkillInput(skill, params);

    // Execute skill with error handling
    try {
      const result = await this.invoke(skillName, validated);

      // Validate output
      return this.validateSkillOutput(skill, result);
    } catch (error) {
      return {
        status: 'failed',
        error: error.message,
        skill: skillName
      };
    }
  }

  getAvailableSkills() {
    return Array.from(this.skills.values()).map(skill => ({
      name: skill.name,
      description: skill.description,
      capabilities: skill.capabilities
    }));
  }
}

// Usage:
const platform = new SkillOrchestrationPlatform();
await platform.registerCustomSkills();

// User request to Claude Code:
// "Implement GDPR compliance for our customer database"

// Claude Code:
// 1. Recognizes this requires multiple specialized skills
// 2. Uses skill orchestration to coordinate execution
// 3. Automatically chains outputs between skills
// 4. Handles errors and retries at skill level
// 5. Generates compliance documentation
```

## Best Practices

1. **Design skills with clear boundaries** - Each skill should handle a distinct domain or capability
2. **Define input/output contracts** - Skills should have clear schemas for inputs and outputs to enable composition
3. **Implement error handling** - Skills should gracefully handle errors and provide meaningful feedback
4. **Make skills reusable** - Design skills to be composable so they work well together in workflows
5. **Document skill capabilities** - Clear documentation of what each skill does enables better orchestration
