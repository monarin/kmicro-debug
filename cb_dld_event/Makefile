# Variables
CC = g++
CFLAGS = -Wall -pthread -I../include -L../lib
LIBS = -lscTDC -ltiff -lsqlite3
CONDA_LIBS = -L$(CONDA_PREFIX)/lib

# Target binary
TARGET = user_callbacks_pipe

# Source files
SRCS = user_callbacks_pipe.cc
OBJS = $(SRCS:.cc=.o)

# Build target
all: $(TARGET)

# Compile source to object files
%.o: %.cc
	$(CC) $(CFLAGS) -c $< -o $@

# Link object files to create the final binary
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS) $(LIBS) $(CONDA_LIBS)

# Clean build files
clean:
	rm -f $(TARGET) $(OBJS)

