variable "subscription_id" {
  type = string
}
variable "location" {
  type = string
}
variable "my_ip" {
  type = string
}
variable "size_haproxy" {
  type = string
}
variable "size_microservices" {
  type = string
}
variable "admin_username" {
  type    = string
  default = "azureuser"
}
variable "public_key_path" {
  type    = string
  default = "/home/vagrant/.ssh/microapp.pub"
}
