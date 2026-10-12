import { useState } from "react";
import "./App.css";

function App() {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [users, setUsers] = useState([]);
  const [message, setMessage] = useState("");

  const API_URL = "http://127.0.0.1:8000";

  // Get users from FastAPI
  const getUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/users`);

      if (!response.ok) {
        throw new Error("Failed to fetch users");
      }

      const data = await response.json();
      setUsers(data);
      setMessage("Users loaded successfully");
    } catch (error) {
      setMessage("Could not connect to backend");
      console.error(error);
    }
  };

  // Save a new user
  const saveUser = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch(`${API_URL}/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: name,
          age: Number(age),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to save user");
      }

      setName("");
      setAge("");
      setMessage("User saved successfully!");

      // Refresh the table after saving
      await getUsers();
    } catch (error) {
      setMessage("Could not save user");
      console.error(error);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <h1>User Management</h1>
        <p className="subtitle">
          React + FastAPI + PostgreSQL
        </p>

        <form onSubmit={saveUser} className="user-form">
          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Age</label>
            <input
              type="number"
              placeholder="Enter your age"
              value={age}
              onChange={(event) => setAge(event.target.value)}
              min="0"
              required
            />
          </div>

          <button type="submit" className="save-btn">
            Save User
          </button>
        </form>

        <div className="table-heading">
          <h2>Saved Users</h2>

          <button onClick={getUsers} className="get-btn">
            Get Users
          </button>
        </div>

        {message && <p className="message">{message}</p>}

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Age</th>
              </tr>
            </thead>

            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan="3" className="empty">
                    Click Get Users to load records
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.name}</td>
                    <td>{user.age}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;
