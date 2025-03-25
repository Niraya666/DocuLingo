FROM doculingo_app:0.0

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
# RUN apt-get update && apt-get install -y vim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice \
    poppler-utils \
    unoconv \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-noto-cjk \
    libmupdf-dev \
    mupdf \
    mupdf-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

    
# Expose port 80 to the outside world
# EXPOSE 80

# 下载 NLTK 数据包
# RUN wget https://utic-public-cf.s3.amazonaws.com/nltk_data.tgz && \
#     mkdir -p /usr/share/nltk_data && \
#     tar -xzf nltk_data.tgz -C /usr/share/nltk_data && \
#     rm nltk_data.tgz

# 设置 NLTK 数据路径环境变量
# ENV NLTK_DATA=/usr/share/nltk_data

# Run main.py when the container launches
# CMD ["python", "app.py"]