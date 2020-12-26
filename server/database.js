const MongoClient = require("mongodb").MongoClient;

let jsonData = require("../config/config.json");
let mongoURI = `mongodb+srv://${jsonData["database"]["username"]}:${jsonData["database"]["password"]}@cluster0.qxcsy.mongodb.net/<dbname>?retryWrites=true&w=majority`;

const connectDB = async () => {
    await MongoClient.connect(mongoURI, { useUnifiedTopology: true })
        .then((client) => {
            console.log("Connected to MongoDB...");
        })
        .catch((error) => console.error(error));
};

module.exports = connectDB;
