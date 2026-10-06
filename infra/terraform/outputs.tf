output "haproxy_public_ip" {
  value = azurerm_public_ip.pip["haproxy"].ip_address
}
output "microservices_public_ip" {
  value = azurerm_public_ip.pip["microservices"].ip_address
}
