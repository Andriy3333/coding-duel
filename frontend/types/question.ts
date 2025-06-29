export interface TestCase {
  input: Record<string, any>;
  expected_output: any;
  is_hidden: boolean;
}

export interface StarterCode {
  python: string;
  javascript: string;
  java: string;
  cpp: string;
}

export interface SolutionApproach {
  time_complexity: string;
  space_complexity: string;
  approach: string;
}

export interface QuestionMetadata {
  acceptance_rate: string;
  total_accepted: string;
  total_submissions: string;
  created_at: string;
  last_updated: string;
}

export interface QuestionData {
  id: string;
  title: string;
  difficulty: string;
  tags: string[];
  description_html: string;
  starter_code: StarterCode;
}
