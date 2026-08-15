import { useEffect, useMemo, useState } from "react";
import "./App.css";

type Coin = {
  id: string;
  name: string;
  symbol: string;
  image?: string;
  market_cap: number;
  fdv: number;
  volume_24h: number;
  tvl: number;
};

type SortOption =
  | "market_cap_desc"
  | "market_cap_asc"
  | "volume_desc"
  | "volume_asc";

function App() {
  const [coins, setCoins] = useState<Coin[]>([]);
  const [search, setSearch] = useState("");
  const [maxFdv, setMaxFdv] = useState("");
  const [sortBy, setSortBy] = useState<SortOption>("market_cap_desc");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/coins")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load projects");
        }

        return response.json();
      })
      .then((data) => {
        setCoins(data);
      })
      .catch((error) => {
        setError(error.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const filteredCoins = useMemo(() => {
    let result = coins.filter((coin) =>
      coin.name.toLowerCase().includes(search.toLowerCase())
    );

    if (maxFdv !== "") {
      const maxFdvNumber = Number(maxFdv);

      if (!Number.isNaN(maxFdvNumber)) {
        result = result.filter((coin) => coin.fdv <= maxFdvNumber);
      }
    }

    return [...result].sort((a, b) => {
      switch (sortBy) {
        case "market_cap_asc":
          return a.market_cap - b.market_cap;

        case "market_cap_desc":
          return b.market_cap - a.market_cap;

        case "volume_asc":
          return a.volume_24h - b.volume_24h;

        case "volume_desc":
          return b.volume_24h - a.volume_24h;

        default:
          return 0;
      }
    });
  }, [coins, search, maxFdv, sortBy]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="container">
      <h1>Crypto Projects</h1>

      <div className="filters">
        <input
          type="text"
          placeholder="Search by project name..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <input
          type="number"
          placeholder="Maximum FDV"
          value={maxFdv}
          onChange={(event) => setMaxFdv(event.target.value)}
        />

        <select
          value={sortBy}
          onChange={(event) => setSortBy(event.target.value as SortOption)}
        >
          <option value="market_cap_desc">
            Market Cap: High to Low
          </option>

          <option value="market_cap_asc">
            Market Cap: Low to High
          </option>

          <option value="volume_desc">
            24h Volume: High to Low
          </option>

          <option value="volume_asc">
            24h Volume: Low to High
          </option>
        </select>
      </div>

      {loading && <p>Loading projects...</p>}

      {error && <p className="error">{error}</p>}

      {!loading && !error && (
        <>
          <p className="result-count">
            Projects found: {filteredCoins.length}
          </p>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Market Cap</th>
                  <th>FDV</th>
                  <th>24h Volume</th>
                  <th>TVL</th>
                </tr>
              </thead>

              <tbody>
                {filteredCoins.map((coin) => (
                  <tr key={coin.id}>
                    <td>
                      <div className="coin">
                        {coin.image && (
                          <img src={coin.image} alt={coin.name} />
                        )}

                        <div>
                          <strong>{coin.name}</strong>
                          <span>{coin.symbol.toUpperCase()}</span>
                        </div>
                      </div>
                    </td>

                    <td>{formatCurrency(coin.market_cap)}</td>
                    <td>{formatCurrency(coin.fdv)}</td>
                    <td>{formatCurrency(coin.volume_24h)}</td>
                    <td>{formatCurrency(coin.tvl)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredCoins.length === 0 && (
            <p>No projects match the selected filters.</p>
          )}
        </>
      )}
    </div>
  );
}

export default App;