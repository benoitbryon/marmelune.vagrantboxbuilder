#!/usr/bin/env python
"""Scripts."""
from optparse import OptionParser
import os

from utils import execute_command, use_temp_dir


class VagrantBoxBuilder(object):
    """Vagrant box builder."""
    def __init__(self):
        self.options = {
            'vm_id': 'tmp_vagrant_1a2b3c4d5e6f7g8h9i',
            'vm_os_type': 'Debian_64',
            'vm_folder': 'var/vm',
            'vm_vram': 16,
            'vm_ram': 512,  # In megabytes.
            'vm_cpus': 1,
            'vm_disk_file': 'var/vm/hdd.vdi',
            'vm_disk_size': 1024*8,  # In megabytes.
            'installer_iso': 'var/debian-squeeze-vagrant-amd64.iso',
            'vagrant_file': '',
            'vagrant_box': 'var/debian-squeeze-vagrant-amd64.box',  # Output box
        }

    def create_box(self):
        """Overall process of box creation and packaging."""
        print "Creating temporary VM."
        self.create_vm()
        print "Installing VM's operating system."
        self.install_iso()
        # Wait for installation to be complete.
        msg = 'Press [enter] when the VM installation is done...'
        raw_input(msg)
        print "Packaging VM into a Vagrant box."
        self.package_box()
        print "Deleting temporary VM."
        self.delete_vm()
        print "Done. Your box has been generated at %(vagrant_box)s" \
              % self.options

    def create_vm(self):
        """Create a new VirtualBox VM."""
        # Create and register box.
        execute_command('VBoxManage createvm --name %(vm_id)s ' \
                        '--ostype %(vm_os_type)s --register ' \
                        '--basefolder "%(vm_folder)s"' % self.options)
        # Set box's ram and cpu.
        execute_command('VBoxManage modifyvm %(vm_id)s --vrde off ' \
                        '--vram %(vm_vram)d --memory %(vm_ram)d ' \
                        '--cpus %(vm_cpus)d' % self.options)
        # Configure hard disk.
        execute_command('VBoxManage storagectl %(vm_id)s --name SATA --add ' \
                        'sata --bootable on' % self.options)
        execute_command('VBoxManage createhd --filename %(vm_disk_file)s ' \
                        '--size %(vm_disk_size)d --format VDI ' \
                        '--variant Standard' % self.options)
        execute_command('VBoxManage storageattach %(vm_id)s ' \
                        '--storagectl SATA --port 0 --device 0 --type hdd ' \
                        '--medium "%(vm_disk_file)s"' % self.options)
        # Add IDE controller
        execute_command('VBoxManage storagectl %(vm_id)s --name IDE --add ' \
                        'ide --controller PIIX4 --hostiocache on ' \
                        '--bootable on' % self.options)

    def install_iso(self):
        """Boot VM on ISO image."""
        # Insert DVD drive into VM.
        execute_command('VBoxManage storageattach %(vm_id)s --storagectl IDE ' \
                        '--type dvddrive --medium %(installer_iso)s --port 0 ' \
                        '--device 0' % self.options)
        # Start VM.
        execute_command('VBoxManage startvm %(vm_id)s --type gui' \
                        % self.options)
        # Ideally, the installation is automatic and the VM is shutdown at the
        # end... but we cannot be sure.

    def delete_vm(self):
        execute_command('VBoxManage unregistervm %(vm_id)s --delete' \
                        % self.options)

    def package_box(self):
        """Package Vagrant box."""
        dirname = os.path.dirname(self.options['vagrant_box'])
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        arguments = ['--base %(vm_id)s', '--output %(vagrant_box)s']
        if self.options['vagrant_file']:
            arguments.append('--vagrantfile %(vagrant_file)s')
        command = 'vagrant package %s' % ' '.join(arguments)
        execute_command(command % self.options)


def main():
    parser = OptionParser()
    builder = VagrantBoxBuilder()
    parser.add_option('--vm-os-type', default=builder.options['vm_os_type'],
                      dest='vm_os_type',
                      help="VM os type. See ``VBoxManage list ostypes``.")
    parser.add_option('--vm-vram', default=builder.options['vm_vram'],
                      dest='vm_vram',
                      help="VM video memory (vram) size, in megabytes.")
    parser.add_option('--vm-ram', default=builder.options['vm_ram'],
                      dest='vm_ram',
                      help="VM memory (RAM) size, in megabytes.")
    parser.add_option('--vm-cpus', default=builder.options['vm_cpus'],
                      dest='vm_cpus',
                      help="VM number of CPUs.")
    parser.add_option('--vm-disk-size', default=builder.options['vm_disk_size'],
                      dest='vm_disk_size',
                      help="VM disk (HDD) size, in megabytes.")
    parser.add_option('--iso', default=builder.options['installer_iso'],
                      dest='installer_iso',
                      help="Path to operating system's installer ISO.")
    parser.add_option('--vagrant-file', default=builder.options['vagrant_file'],
                      dest='vagrant_file',
                      help="Path to Vagrantfile.")
    parser.add_option('--vagrant-box', default=builder.options['vagrant_box'],
                      dest='vagrant_box',
                      help="Path for the output box file.")
    (options, args) = parser.parse_args()
    for option in ['vm_os_type', 'vm_vram', 'vm_ram', 'vm_cpus',
                   'vm_disk_size', 'installer_iso', 'vagrant_file',
                   'vagrant_box']:
        builder.options[option] = getattr(options, option)
    for option in ['vm_vram', 'vm_ram', 'vm_cpus']:  # Int conversion.
        builder.options[option] = int(builder.options[option])
    required_files = {'--vagrant-file': 'vagrant_file',
                      '--iso': 'installer_iso'}
    if not os.path.exists(builder.options['installer_iso']):
        parser.error("Input file \"%s\" doesn't exists (see option %s)." \
                     % (builder.options['installer_iso'], '--iso'))
    if builder.options['vagrant_file'] \
       and not os.path.exists(builder.options['installer_iso']):
        parser.error("Input file \"%s\" doesn't exists (see option %s)." \
                     % (builder.options['vagrant_file'], '--vagrant-file'))
    with use_temp_dir() as vm_folder:
        builder.options['vm_folder'] = vm_folder
        builder.options['vm_disk_file'] = os.path.join(vm_folder, 'hdd.vdi')
        builder.create_box()


if __name__ == '__main__':
    main()