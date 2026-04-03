export interface Worker {
  id: number;
  phone: string;
  name: string;
  delivery_platform: string;
  platform_id: string;
  city_id: number;
  primary_zone_id: number;
  upi_id: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface City {
  id: number;
  name: string;
  tier: number;
  risk_multiplier: number;
}

export interface Zone {
  id: number;
  name: string;
  city_id: number;
  latitude: number;
  longitude: number;
  disruption_rate_12m: number;
  risk_score: number;
}

export interface Policy {
  id: number;
  worker_id: number;
  zone_id: number;
  coverage_hours: number;
  weekly_premium: number;
  status: string;
  coverage_start_date: string;
  coverage_end_date: string | null;
  created_at: string;
}

export interface Claim {
  id: number;
  worker_id: number;
  policy_id: number;
  disruption_event_id: number;
  amount: number;
  status: string;
  fraud_score: number | null;
  fraud_confidence: string | null;
  payout_status: string;
  payout_transaction_id: string | null;
  review_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface DisruptionEvent {
  id: number;
  zone_id: number;
  trigger_type: string;
  severity: string;
  start_time: string;
  end_time: string | null;
  data: Record<string, unknown> | null;
  is_verified: boolean;
  created_at: string;
}

export interface PremiumCalculation {
  weekly_premium: number;
  base_premium: number;
  city_risk_factor: number;
  zone_risk_factor: number;
  coverage_factor: number;
}

export interface Stats {
  total_workers: number;
  active_policies: number;
  total_claims: number;
  approved_claims: number;
  pending_claims: number;
  total_payouts: number;
  loss_ratio: number;
}

export interface EarningsHistory {
  avg_daily: number;
  avg_hourly: number;
  total_days: number;
  total_earnings: number;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role?: string;
}
