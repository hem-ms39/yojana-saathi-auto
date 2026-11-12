import { createBrowserClient } from "@supabase/ssr";

export function createSupabaseClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// Singleton for use in hooks/components
let _client: ReturnType<typeof createSupabaseClient> | null = null;
export function getSupabase() {
  if (!_client) _client = createSupabaseClient();
  return _client;
}
