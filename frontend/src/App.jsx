import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

const Button = ({ onClick, children, loading }) => {
  return (
    <motion.button
      onClick={onClick}
      className="w-fit px-6 py-3 mt-4 flex flex-col items-center justify-center gap-1 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 focus:outline-none transition-all"
    >
      {loading ? "Running..." : children}
    </motion.button>
  );
};

const Card = ({ children }) => {
  return (
    <div className="bg-white shadow-lg rounded-lg p-6 mt-6 w-full max-w-lg">
      {children}
    </div>
  );
};

const Text = ({ children, className }) => {
  return <p className={`text-base ${className}`}>{children}</p>;
};

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const runScript = async () => {
    setLoading(true);
    await axios.get("https://twittrend-web-scrapping.onrender.com/api/run-script");
    const res = await axios.get("https://twittrend-web-scrapping.onrender.com/api/latest-trend");
    setData(res.data);
    setLoading(false);
  };

  const fetchRandomFile = async () => {
    try {
      const res = await axios.get("https://twittrend-web-scrapping.onrender.com/api/random-file");
      setData(res.data);
    } catch (error) {
      console.error("Error fetching random file:", error);
    }
  };

  return (
    <div className="flex flex-col items-center p-10 bg-gradient-to-b from-white to-gray-100 min-h-screen">
      <Button onClick={runScript} loading={loading}>
        Click here to run the script
      </Button>

      {data && (
        <Card>
          <Text className="text-xl font-semibold text-center text-gray-800">
            Trending Topics as of {data.end_time}
          </Text>
          <div className="mt-4 space-y-3">
            <div className="border border-gray-200 p-3 rounded-lg">
              <Text className="text-lg font-medium text-gray-800">
                {data.trend1}
              </Text>
            </div>
            <div className="border border-gray-200 p-3 rounded-lg">
              <Text className="text-lg font-medium text-gray-800">
                {data.trend2}
              </Text>
            </div>
            <div className="border border-gray-200 p-3 rounded-lg">
              <Text className="text-lg font-medium text-gray-800">
                {data.trend3}
              </Text>
            </div>
            <div className="border border-gray-200 p-3 rounded-lg">
              <Text className="text-lg font-medium text-gray-800">
                {data.trend4}
              </Text>
            </div>
            <div className="border border-gray-200 p-3 rounded-lg">
              <Text className="text-lg font-medium text-gray-800">
                {data.trend5}
              </Text>
            </div>
          </div>
          <Text className="mt-4 text-center text-sm text-gray-600">
            The IP address used for this query was{" "}
            <strong>{data.ip_address}</strong>
          </Text>
          <pre className="text-xs bg-gray-200 p-3 rounded-md mt-4">
            {JSON.stringify(data, null, 2)}
          </pre>

          <div className="w-full text-center">
            <button
              onClick={fetchRandomFile}
              loading={loading}
              className="w-full px-6 py-3 mt-4 flex flex-col items-center justify-center gap-1 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 focus:outline-none transition-all"
            >
              Run the same script Again
            </button>
            <span className="text-sm text-black">
              It will fetch a random file
            </span>
          </div>
        </Card>
      )}
    </div>
  );
}

export default App;
