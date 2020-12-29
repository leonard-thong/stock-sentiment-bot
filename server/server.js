const express = require("express");
const MongoClient = require("mongodb").MongoClient;

let jsonData = require("../config/config.json");
let mongoURI = `mongodb+srv://${jsonData["database"]["username"]}:${jsonData["database"]["password"]}@cluster0.qxcsy.mongodb.net/<dbname>?retryWrites=true&w=majority`;

const app = express();

app.use(express.json());

const connectDB = async () => {
    await MongoClient.connect(mongoURI, { useUnifiedTopology: true })
        .then((client) => {
            console.log("Connected to MongoDB...");

            var db = client.db("results");

            var query = { _id: "20201226" };
            var data;
            db.collection("results")
                .find(query)
                .toArray(function (err, result) {
                    if (err) throw err;

                    data = result[0];
                });

            app.use("/", (req, res) => {
                res.jsonp(data);
            });
        })
        .catch((error) => console.error(error));
};

// Connect Database
connectDB();

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
