const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const { exec } = require("child_process");
const path = require("path");
require("dotenv").config();

const app = express();
app.use(cors());
app.use(express.json());

mongoose
  .connect(process.env.MONGO_URI)
  .then(() => {
    console.log("MongoDB connected successfully!");
  })
  .catch((error) => {
    console.error("Error connecting to MongoDB:", error);
  });

//Without ProxyMesh
app.get("/api/run-script", (req, res) => {
  exec("python twitter_trending_scraper.py", (error, stdout, stderr) => {
    if (error) return res.status(500).send(`Error: ${stderr}`);
    res.send("Script executed successfully!");
  });
});

// //With ProxyMesh
// app.get("/api/run-script", (req, res) => {
//   exec(
//     "python twitter_trending_scraper_with_proxymesh.py",
//     (error, stdout, stderr) => {
//       if (error) return res.status(500).send(`Error: ${stderr}`);
//       res.send("Script executed successfully!");
//     }
//   );
// });

app.get("/api/latest-trend", async (req, res) => {
  try {
    const db = mongoose.connection.useDb("twitter_scraper");
    const latest = await db
      .collection("trending_topics")
      .findOne({}, { sort: { end_time: -1 } });
    if (!latest) {
      return res.status(404).send("No trending topics found.");
    }
    res.json(latest);
  } catch (error) {
    console.error("Error fetching the latest trend:", error);
    res.status(500).send("Error fetching the latest trend");
  }
});

app.get("/api/random-file", async (req, res) => {
  try {
    const db = mongoose.connection.useDb("twitter_scraper");
    const randomFile = await db
      .collection("trending_topics")
      .aggregate([{ $sample: { size: 1 } }])
      .toArray();

    if (randomFile.length > 0) {
      res.json(randomFile[0]);
    } else {
      res.status(404).send("No random file found.");
    }
  } catch (error) {
    console.error("Error fetching random file:", error);
    res.status(500).send("Error fetching random file");
  }
});

if (process.env.NODE_ENV === "production") {
  app.use(express.static(path.join(__dirname, "../frontend/dist")));

  app.get("*", (req, res) => {
    res.sendFile(path.resolve(__dirname, "../frontend/dist/index.html"));
  });
}

app.listen(3001, () => console.log("Server running on port 3001"));
