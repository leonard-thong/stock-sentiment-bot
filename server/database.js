const mongoose = require("mongoose");

let jsonData = require("../config/config.json");
let mongoURI = `mongodb+srv://${jsonData["database"]["username"]}:${jsonData["database"]["password"]}@cluster0.qxcsy.mongodb.net/<dbname>?retryWrites=true&w=majority`

const connectDB = async () => {
    try {
        await mongoose.connect(
            mongoURI,
            {
                useNewUrlParser: true,
                useCreateIndex: true,
                useFindAndModify: false,
                useUnifiedTopology: true,
            }
        );

        console.log("MongoDB Connected...");
    } catch (err) {
        console.error(err.message);
        // Exit process with failure
        process.exit(1);
    }
};

module.exports = connectDB;
