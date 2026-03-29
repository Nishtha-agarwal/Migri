import { useEffect, useState } from "react";
import API from "../api";

export default function Dashboard() {
  const [features, setFeatures] = useState([]);
  const [usage, setUsage] = useState(0);
  const [role, setRole] = useState("user");

  useEffect(() => {
    fetchFeatures();
    fetchUsage();
    setRole("admin"); // demo (later from backend)
  }, []);

  const fetchFeatures = async () => {
    const res = await API.get("/features");
    setFeatures(res.data);
  };

  const fetchUsage = async () => {
    const res = await API.get("/usage"); // create this API
    setUsage(res.data.used);
  };

  const createProject = async () => {
    try {
      const res = await API.post("/create_project");
      alert(res.data.msg);
      fetchUsage();
    } catch (err) {
      alert(err.response.data.msg);
    }
  };

  const upgradePlan = async () => {
    await API.post("/upgrade"); // backend endpoint
    alert("Upgraded to Pro 🚀");
    fetchFeatures();
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* Usage */}
      <div className="mt-4 p-4 bg-gray-100 rounded">
        <p>Usage: {usage}</p>
      </div>

      {/* Features */}
      <div className="grid grid-cols-2 gap-4 mt-4">
        {features.map((f, i) => (
          <div key={i} className="p-4 bg-white shadow rounded">
            {f}
          </div>
        ))}
      </div>

      {/* Actions */}
      <button
        onClick={createProject}
        className="mt-4 bg-green-500 text-white px-4 py-2 rounded"
      >
        Create Project
      </button>

      {/* Upgrade */}
      <button
        onClick={upgradePlan}
        className="mt-4 ml-2 bg-purple-500 text-white px-4 py-2 rounded"
      >
        Upgrade to Pro
      </button>

      {/* Role-based UI */}
      {role === "admin" && (
        <div className="mt-6 p-4 bg-yellow-100 rounded">
          <h2 className="font-bold">Admin Panel</h2>
          <p>Manage users & subscriptions</p>
        </div>
      )}
    </div>
  );
}