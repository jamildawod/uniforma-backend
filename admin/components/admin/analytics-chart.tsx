"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { CategoryBreakdown } from "@/types/intelligence";

export function AnalyticsChart({ data }: { data: CategoryBreakdown[] }) {
  return (
    <div className="h-[320px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 12, right: 12, left: 0, bottom: 12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#dbe4ef" />
          <XAxis dataKey="category" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
          <Tooltip
            cursor={{ fill: "rgba(16,35,63,0.06)" }}
            contentStyle={{ borderRadius: 16, borderColor: "#dbe4ef", boxShadow: "0 20px 40px rgba(16,35,63,0.08)" }}
          />
          <Bar dataKey="total_products" fill="#10233f" radius={[12, 12, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
