CREATE TABLE "MOVIMIENTOS" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "date" TEXT NOT NULL,
        "time" TEXT NOT NULL,
        "currency_from" TEXT NOT NULL,
        "amount_from" REAL NOT NULL,
        "currency_to" TEXT NOT NULL,
        "amount_to" REAL NOT NULL
)
