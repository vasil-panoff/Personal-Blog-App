FROM public.ecr.aws/amazonlinux/amazonlinux:2

# Install Python & pip
RUN yum install -y python3 python3-pip && yum clean all

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 5000

CMD ["python3", "app.py"]
