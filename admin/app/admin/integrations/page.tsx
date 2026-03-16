import { redirect } from "next/navigation";

export default function AdminIntegrationsIndexPage() {
  redirect("/admin/settings/integrations");
}
