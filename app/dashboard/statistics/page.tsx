import { getDashboardStats } from "@/lib/api";

interface DashboardStats {
  total_trades: number;
  open_trades: number;
  closed_trades: number;
  wins: number;
  losses: number;
  win_rate: number;
  total_rr: number;
  average_rr: number;
  total_profit: number;
}

export default async function StatisticsPage() {
  const stats = (await getDashboardStats()) as DashboardStats;

  const cards = [
    ["Total Trades", stats.total_trades],
    ["Open Trades", stats.open_trades],
    ["Closed Trades", stats.closed_trades],
    ["Wins", stats.wins],
    ["Losses", stats.losses],
    ["Win Rate", `${stats.win_rate}%`],
    ["Total RR", stats.total_rr],
    ["Average RR", stats.average_rr],
    ["Total Profit", `$${stats.total_profit}`],
  ];

  return (
    <main className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">
          Statistics
        </h1>

        <p className="mt-2 text-slate-400">
          Overall performance of the Blissfinity AI Signal Bot.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {cards.map(([title, value]) => (
          <div
            key={title}
            className="rounded-xl border border-slate-800 bg-slate-900 p-6"
          >
            <p className="text-sm text-slate-400">
              {title}
            </p>

            <p className="mt-3 text-3xl font-bold text-white">
              {value}
            </p>
          </div>
        ))}
      </div>
    </main>
  );
}