"use client"

import { useEffect, useState } from "react"

import type { SupplierSyncLog, SupplierSyncOverview } from "@/lib/types/pim"

type SupplierSyncMonitorProps = {
  initialOverview?: SupplierSyncOverview
  role?: "admin" | "editor"
}

export default function SupplierSyncMonitor({ initialOverview }: SupplierSyncMonitorProps) {
  const [logs, setLogs] = useState<SupplierSyncLog[]>(initialOverview?.logs ?? [])

  useEffect(() => {
    fetch("/api/v1/admin/integrations/sync")
      .then(res => res.json())
      .then((data: SupplierSyncOverview) => setLogs(data.logs ?? []))
  }, [])

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">
        Supplier Sync Monitor
      </h2>

      <table className="w-full border">
        <thead>
          <tr>
            <th>Supplier</th>
            <th>Status</th>
            <th>Products</th>
            <th>Images</th>
            <th>Started</th>
          </tr>
        </thead>

        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>{log.supplier}</td>
              <td>{log.status}</td>
              <td>{log.products_imported}</td>
              <td>{log.images_downloaded}</td>
              <td>{log.started_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
