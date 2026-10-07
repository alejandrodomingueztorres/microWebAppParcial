apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-__NAME__
  namespace: microapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql-__NAME__
  template:
    metadata:
      labels:
        app: mysql-__NAME__
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          ports:
            - containerPort: 3306
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: __NAME__-db-password
            - name: MYSQL_DATABASE
              value: __NAME___db
          volumeMounts:
            - name: init
              mountPath: /docker-entrypoint-initdb.d
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
            limits:
              memory: "768Mi"
      volumes:
        - name: init
          configMap:
            name: __NAME__-db-init
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-__NAME__
  namespace: microapp
spec:
  selector:
    app: mysql-__NAME__
  ports:
    - port: 3306
      targetPort: 3306
