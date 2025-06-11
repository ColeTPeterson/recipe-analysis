// Check if MONGO_INITDB_DATABASE is set
const dbName = process.env.MONGO_INITDB_DATABASE;
if (!dbName) {
    print('MONGO_INITDB_DATABASE env. variable not set, exiting');
    quit(1);
}

db = db.getSiblingDB(dbName)
print(`Initializing database: ${dbName}`);

const dataDir = '/init-data/structured/';
const collectionName = 'recipes';

// Create the Collection
try {
    if (!db.getCollectionNames().includes(collectionName)) {
        db.createCollection(collectionName);
        print(`Created collection ${collectionName}`);
    }
    else {
        print(`Collection ${collectionName} already exists, skipping`);
    }
}
catch (e) {
    printerr(`ERROR: collection ${collectionName} could not be created: ${e}`);
    quit(1)
}

// Import data from JSON project files
print(`Importing all files from ${dataDir} as JSON objects`)
try {
    const files = fs.readdirSync(dataDir);

    files.forEach(file => {
        const filePath = dataDir + file;
        try {
            const fileContent = fs.readFileSync(filePath, 'utf8');
            const recipeData = JSON.parse(fileContent);
            db[collectionName].insertOne(recipeData);
        }
        catch (e) {
            printerr(`    ERROR: File ${filePath} could not be processed: ${e}`);
        }
    });
}
catch (e) {
    printerr(`ERROR: Directory ${dataDir} could not be read: ${e}`);
    quit(1);
}

print(`Finished importing files into collection: ${collectionName}`);