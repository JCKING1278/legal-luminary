# Build candidates HTML generator. Run 'make install' to write _includes/candidates-table.html
CC = cc
CFLAGS = -Wall -Wextra
BIN = candidates_gen
INCLUDES_DIR = ../_includes

all: $(BIN)

$(BIN): candidates.c candidates.h
	$(CC) $(CFLAGS) -o $(BIN) candidates.c

install: $(BIN)
	./$(BIN) > $(INCLUDES_DIR)/candidates-table.html
	@echo "Written $(INCLUDES_DIR)/candidates-table.html"

clean:
	rm -f $(BIN)

.PHONY: all install clean
