import { Requirement, RequirementType, ParsedDocument, DocumentSection } from '../types';
import { logger } from '../utils/logger';

export class RequirementsAnalyzer {
  private requirements: Requirement[] = [];
  private requirementCounter = 0;

  analyze(document: ParsedDocument): Requirement[] {
    logger.info('Starting requirement analysis...');
    this.requirements = [];
    this.requirementCounter = 0;

    const text = document.text;
    const sections = document.sections;

    this.extractFromText(text);
    this.extractFromSections(sections);
    this.deduplicate();
    this.generateIds();

    logger.info(`Extracted ${this.requirements.length} requirements`);
    return this.requirements;
  }

  private extractFromText(text: string): void {
    const lines = text.split('\n').map(l => l.trim()).filter(l => l);

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const lower = line.toLowerCase();

      const patterns: Array<{ type: RequirementType; match: RegExp }> = [
        { type: RequirementType.BUSINESS, match: /business requirement|brd|business need|business goal/i },
        { type: RequirementType.FUNCTIONAL, match: /functional requirement|shall|must|should|will|the system (should|must|shall|will|need to)/i },
        { type: RequirementType.NON_FUNCTIONAL, match: /non.functional|performance|scalability|availability|reliability|response time|throughput/i },
        { type: RequirementType.USER_STORY, match: /as a|i want|so that|user story|story:|scenario:/i },
        { type: RequirementType.UI, match: /ui requirement|user interface|screen|page should|button|dropdown|input field|display|show|render/i },
        { type: RequirementType.API, match: /api|endpoint|rest|soap|graphql|get request|post request|put request|delete request/i },
        { type: RequirementType.VALIDATION, match: /validation|must be valid|must not|required field|mandatory|should not allow|error message/i },
        { type: RequirementType.BUSINESS_RULE, match: /business rule|rule:|if.*then|condition|eligibility|approval|workflow rule/i },
        { type: RequirementType.INTEGRATION, match: /integration|third.party|external system|connect|sync|webhook|callback/i },
        { type: RequirementType.ERROR_HANDLING, match: /error handling|error message|exception|failover|retry|fallback|error code/i },
        { type: RequirementType.SECURITY, match: /security|authentication|authorization|login|password|role|permission|encrypt|token|oauth|jwt/i },
        { type: RequirementType.BOUNDARY, match: /boundary|limit|maximum|minimum|range|between.*and|up to|at least|at most/i },
        { type: RequirementType.EDGE_CASE, match: /edge case|special case|unusual|exceptional|corner case/i },
      ];

      for (const pattern of patterns) {
        if (pattern.match.test(lower)) {
          const nextLines = lines.slice(i, Math.min(i + 5, lines.length)).join('. ');
          this.addRequirement(nextLines, pattern.type);
          break;
        }
      }

      if (/(^\d+[\)\.])|(^[a-z][\)\.])|(^-)/i.test(line) && line.length > 20) {
        this.addRequirement(line, RequirementType.FUNCTIONAL);
      }
    }
  }

  private extractFromSections(sections: DocumentSection[]): void {
    for (const section of sections) {
      if (section.data && section.data.length > 0) {
        for (const row of section.data) {
          const rowText = Object.values(row).join(' ');
          if (rowText.length > 20) {
            this.addRequirement(rowText, RequirementType.FUNCTIONAL);
          }
        }
      }

      if (section.header) {
        const headerLower = section.header.toLowerCase();
        if (
          headerLower.includes('requirement') ||
          headerLower.includes('user story') ||
          headerLower.includes('specification') ||
          headerLower.includes('feature')
        ) {
          const subLines = section.text.split('\n').filter(l => l.trim());
          for (const line of subLines) {
            if (line.length > 20 && !line.startsWith('#')) {
              this.addRequirement(line, RequirementType.FUNCTIONAL);
            }
          }
        }
      }
    }
  }

  private addRequirement(text: string, type: RequirementType): void {
    const cleanText = text.replace(/^[#*\-\d\)\.\s]+/, '').trim();
    if (cleanText.length < 15) return;

    const exists = this.requirements.some(
      r => r.description.toLowerCase() === cleanText.toLowerCase()
    );
    if (exists) return;

    const acceptanceCriteria = this.extractAcceptanceCriteria(text);
    const dependencies = this.extractDependencies(text);

    this.requirements.push({
      id: '',
      description: cleanText,
      type,
      category: this.categorize(type, cleanText),
      source: '',
      priority: this.determinePriority(type, cleanText),
      acceptanceCriteria,
      dependencies,
    });
  }

  private extractAcceptanceCriteria(text: string): string[] {
    const criteria: string[] = [];
    const lower = text.toLowerCase();

    if (lower.includes('given') || lower.includes('when') || lower.includes('then')) {
      const parts = text.split(/\n|\.\s/);
      for (const part of parts) {
        const trimmed = part.trim();
        if (
          trimmed.toLowerCase().startsWith('given') ||
          trimmed.toLowerCase().startsWith('when') ||
          trimmed.toLowerCase().startsWith('then') ||
          trimmed.toLowerCase().startsWith('and')
        ) {
          criteria.push(trimmed);
        }
      }
    }

    const verifyMatch = text.match(/verify|validate|ensure|check|confirm/i);
    if (verifyMatch) {
      criteria.push(text);
    }

    return criteria;
  }

  private extractDependencies(text: string): string[] {
    const dependencies: string[] = [];
    const depMatch = text.match(/(?:depends? on|requires?|integration with|using|after|prerequisite)s?\s+([^.]+)/gi);
    if (depMatch) {
      depMatch.forEach(d => dependencies.push(d.trim()));
    }
    return dependencies;
  }

  private categorize(type: RequirementType, text: string): string {
    const lower = text.toLowerCase();
    if (lower.includes('login') || lower.includes('authentication') || lower.includes('user management')) return 'Authentication';
    if (lower.includes('payment') || lower.includes('checkout') || lower.includes('cart')) return 'Payment';
    if (lower.includes('search') || lower.includes('filter') || lower.includes('sort')) return 'Search';
    if (lower.includes('report') || lower.includes('dashboard') || lower.includes('analytics')) return 'Reporting';
    if (lower.includes('email') || lower.includes('notification') || lower.includes('alert')) return 'Notification';
    if (lower.includes('profile') || lower.includes('account') || lower.includes('setting')) return 'Account Management';
    if (lower.includes('upload') || lower.includes('download') || lower.includes('import') || lower.includes('export')) return 'File Management';
    if (lower.includes('api') || lower.includes('endpoint') || lower.includes('webhook')) return 'API';
    return type;
  }

  private determinePriority(type: RequirementType, text: string): string {
    const lower = text.toLowerCase();
    if (
      lower.includes('critical') ||
      lower.includes('must') ||
      lower.includes('required') ||
      lower.includes('essential') ||
      type === RequirementType.SECURITY
    ) {
      return 'High';
    }
    if (lower.includes('should')) return 'Medium';
    if (lower.includes('could') || lower.includes('nice') || lower.includes('optional')) return 'Low';
    return 'Medium';
  }

  private deduplicate(): void {
    const seen = new Set<string>();
    this.requirements = this.requirements.filter(r => {
      const key = r.description.toLowerCase().substring(0, 100);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  private generateIds(): void {
    this.requirements.forEach((req, index) => {
      req.id = `REQ${String(index + 1).padStart(3, '0')}`;
    });
  }

  getSummary(): Record<string, number> {
    const summary: Record<string, number> = {};
    for (const req of this.requirements) {
      const key = req.type;
      summary[key] = (summary[key] || 0) + 1;
    }
    return summary;
  }
}
