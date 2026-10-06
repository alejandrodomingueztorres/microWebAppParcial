locals {
  vms = {
    haproxy = {
      name = "vm-haproxy"
      size = var.size_haproxy
      ip   = "10.0.1.10"
    }
    microservices = {
      name = "vm-microservices"
      size = var.size_microservices
      ip   = "10.0.1.11"
    }
  }
}

# --- Grupo de recursos y red ---
resource "azurerm_resource_group" "rg" {
  name     = "micro-proyecto2"
  location = var.location
}

resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-mp2"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "subnet" {
  name                 = "subnet-mp2"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# --- Firewall: solo SSH y stats desde tu IP, HTTP abierto ---
resource "azurerm_network_security_group" "nsg" {
  name                = "nsg-mp2"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "http"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "haproxy-stats"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "assoc" {
  subnet_id                 = azurerm_subnet.subnet.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

# --- IPs públicas, tarjetas de red y VMs ---
resource "azurerm_public_ip" "pip" {
  for_each            = local.vms
  name                = "pip-${each.value.name}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_interface" "nic" {
  for_each            = local.vms
  name                = "nic-${each.value.name}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Static"
    private_ip_address            = each.value.ip
    public_ip_address_id          = azurerm_public_ip.pip[each.key].id
  }
}

resource "azurerm_linux_virtual_machine" "vm" {
  for_each                        = local.vms
  name                            = each.value.name
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = azurerm_resource_group.rg.location
  size                            = each.value.size
  admin_username                  = var.admin_username
  network_interface_ids           = [azurerm_network_interface.nic[each.key].id]
  disable_password_authentication = true
  admin_ssh_key {
    username   = var.admin_username
    public_key = file(var.public_key_path)
  }


  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }
 }
# --- Terraform escribe el inventario de Ansible ---
resource "local_file" "inventory" {
  filename = "${path.module}/../ansible/inventory.ini"
  content  = <<-EOT
    [haproxy]
    vm-haproxy ansible_host=${azurerm_public_ip.pip["haproxy"].ip_address}

    [microservices]
    vm-microservices ansible_host=${azurerm_public_ip.pip["microservices"].ip_address}

    [all:vars]
    ansible_user=${var.admin_username}
    ansible_ssh_private_key_file=~/.ssh/microapp
    microservices_private_ip=${local.vms["microservices"].ip}
  EOT
}

# --- Terraform lanza Ansible al terminar ---
resource "null_resource" "ansible" {
  depends_on = [azurerm_linux_virtual_machine.vm, local_file.inventory]

  triggers = {
    vm_ids   = join(",", [for v in azurerm_linux_virtual_machine.vm : v.id])
    playbook = filesha256("${path.module}/../ansible/site.yml")
  }

  provisioner "local-exec" {
    command     = "sleep 60 && ansible-playbook site.yml"
    working_dir = "${path.module}/../ansible"
  }
}
