'''

	The settings for OSMC are handled by the OSMC Settings Addon (OSA).

	In order to more easily accomodate future changes and enhancements, each OSMC settings bundle (module) is a separate addon.
	The module can take the form of an xbmc service, an xbmc script, or an xbmc module, but it must be installed into the users'
	/usr/share/kodi/addons folder.

	The OSA collects the modules it can find, loads their icons, and launches them individually when the user clicks on an icon.

	The modules can either have their own GUI, or they can leverage the settings interface provided by XBMC. If the OSG uses the XBMC 
	settings interface, then all of their settings must be stored in the addons settings.xml. This is true even if the source of record
	is a separate config file.

	An example of this type is the Pi settings module; the actual settings are read from the config.txt, then written to the 
	settings.xml for display in kodi, then finally all changes are written back to the config.txt. The Pi module detects user 
	changes to the settings by identifying the differences between a newly read settings.xml and the values from a previously 
	read settings.xml.

	The values of the settings displayed by this module are only ever populated by the items in the settings.xml. [Note: meaning that 
	if the settings data is retrieved from a different source, it will need to be populated in the module before it is displayed
	to the user.]

	Each module must have in its folder, a sub-folder called 'resources/osmc'. Within that folder must reside this script (OSMCSetting.py), 
	and the icons to be used in the OSG to represent the module (FX_Icon.png and FO_Icon.png for unfocused and focused images
	respectively).

	When the OSA creates the OSMC Settings GUI (OSG), these modules are identified and the OSMCSetting.py script in each of them 
	is imported. This script provides the mechanism for the OSG to apply the changes required from a change in a setting.

	The OSMCSetting.py file must have a class called OSMCSettingClass as shown below.

	The key variables in this class are:

		addonid							: The id for the addon. This must be the id declared in the addons addon.xml.

		description 					: The description for the module, shown in the OSA

		reboot_required					: A boolean to declare if the OS needs to be rebooted. If a change in a specific setting 
									 	  requires an OS reboot to take affect, this is flag that will let the OSG know.

		setting_data_method 			: This dictionary contains:
												- the name of all settings in the module
												- the current value of those settings
												- [optional] apply - a method to call for each setting when the value changes
												- [optional] translate - a method to call to translate the data before adding it to the 
												  setting_data_method dict. The translate method must have a 'reverse' argument which 
												  when set to True, reverses the transformation.  



	The key methods of this class are:

		open_settings_window			: This is called by the OSG when the icon is clicked. This will open the settings window.
										  Usually this would be __addon__.OpenSettings(), but it could be any other script.
										  This allows the creation of action buttons in the GUI, as well as allowing developers 
										  to script and skin their own user interfaces.

		[optional] first_method			: called before any individual settings changes are applied.

		[optional] final_method			: called after all the individual settings changes are done.

		[optional] boot_method			: called when the OSA is first started.

		apply_settings					: This is called by the OSG to apply the changes to any settings that have changed.
										  It calls the first setting method, if it exists. 
										  Then it calls the method listed in setting_data_method for each setting. Then it 
										  calls the final method, again, if it exists.

		populate_setting_data_method	: This method is used to populate the setting_data_method with the current settings data.
										  Usually this will be from the addons setting data stored in settings.xml and retrieved
										  using the settings_retriever_xml method.

										  Sometimes the user is able to edit external setting files (such as the Pi's config.txt).
										  If the developer wants to use this source in place of the data stored in the
										  settings.xml, then they should edit this method to include a mechanism to retrieve and 
										  parse that external data. As the window shown in the OSG populates only with data from 
										  the settings.xml, the developer should ensure that the external data is loaded into that
										  xml before the settings window is opened.

		settings_retriever_xml			: This method is used to retrieve all the data for the settings listed in the 
										  setting_data_method from the addons settings.xml.

	The developer is free to create any methods they see fit, but the ones listed above are specifically used by the OSA. 
	Specifically, the apply_settings method is called when the OSA closes. 

	Settings changes are applied when the OSG is called to close. But this behaviour can be changed to occur when the addon
	settings window closes by editing the open_settings_window. The method apply_settings will still be called by OSA, so 
	keep that in mind.

'''


# XBMC Modules
import xbmcaddon
import xbmcgui
import xbmc

import sys
import os
import threading

addonid = "script.module.osmcsetting.services"
__addon__  = xbmcaddon.Addon(addonid)

# Custom modules
sys.path.append(xbmc.translatePath(os.path.join(xbmcaddon.Addon(addonid).getAddonInfo('path'), 'resources','lib')))

# OSMC SETTING Modules
from service_selection_gui import service_selection

def log(message):

	try:
		message = str(message)
	except UnicodeEncodeError:
		message = message.encode('utf-8', 'ignore' )

	xbmc.log('OSMC SERVICES ' + str(message), level=xbmc.LOGDEBUG)


class OSMCSettingClass(threading.Thread):

	''' 
		A OSMCSettingClass is way to substantiate the settings of an OSMC settings module, and make them available to the 
		OSMC Settings Addon (OSA).

	'''

	def __init__(self):

		''' 
			The setting_data_method contains all the settings in the settings group, as well as the methods to call when a
			setting_value has changed and the existing setting_value. 
		'''

		super(OSMCSettingClass, self).__init__()

		self.addonid = "script.module.osmcsetting.services"
		self.me = xbmcaddon.Addon(self.addonid)

		# this is what is displayed in the main settings gui
		self.shortname = 'Services'

		self.description = 	"""
								This is the text that is shown on the OSG. It should describe what the settings module is for,
								the settings it controls, and anything else you want, I suppose.
							"""

		self.setting_data_method = 	{

									'none': 	{
														'setting_value' : '',
														}								

									}

		# populate the settings data in the setting_data_method
		self.populate_setting_data_method()


		# a flag to determine whether a setting change requires a reboot to take effect
		self.reboot_required = False




	def populate_setting_data_method(self):

		'''
			Constructs list of service tuples (service name, status[active, inactive]).
		'''

		pass


	def run(self):

		'''
			The method that determines what happens when the item is clicked in the settings GUI.
			Usually this would be __addon__.OpenSettings(), but it could be any other script.
			This allows the creation of action buttons in the GUI, as well as allowing developers to script and skin their 
			own user interfaces.
		'''

		me = xbmcaddon.Addon(self.addonid)
		scriptPath = me.getAddonInfo('path')

		# 						( s_entry, service_name, running, enabled )

		service_list = {'test1b': ('test1', 'test1a', ' (running)', True), 'test2b': ('test2','test2a', ' (enabled)', True), 'test3b': ('test3', 'test3a', '', False)}

		xml = "ServiceBrowser_720OSMC.xml" if xbmcgui.Window(10000).getProperty("SkinHeight") == '720' else "ServiceBrowser_OSMC.xml"

		creation = service_selection(xml, scriptPath, 'Default', service_list=service_list, logger=log)
		creation.doModal()
		del creation


	def apply_settings(self):

		'''
			This method will apply all of the settings. It calls the first_method, if it exists. 
			Then it calls the method listed in setting_data_method for each setting. Then it calls the
			final_method, again, if it exists.
		'''

		pass


	def settings_retriever_xml(self):

		''' 
			Reads the stored settings (in settings.xml) and returns a dictionary with the setting_name: setting_value. This 
			method cannot be overwritten.
		'''

		pass


	##############################################################################################################################
	#																															 #
	def first_method(self):

		''' 
			The method to call before all the other setting methods are called.

			For example, this could be a call to stop a service. The final method could then restart the service again. 
			This can be used to apply the setting changes.

		'''	

		pass


	def final_method(self):

		''' 
			The method to call after all the other setting methods have been called.

			For example, in the case of the Raspberry Pi's settings module, the final writing to the config.txt can be delayed
			until all the settings have been updated in the setting_data_method. 

		'''

		pass


	def boot_method(self):

		''' 
			The method to call when the OSA is first activated (on reboot)

		'''

		pass

	#																															 #
	##############################################################################################################################


	##############################################################################################################################
	#																															 #

	''' 
		Methods beyond this point are for specific settings. 
	'''

	# SETTING METHOD
	def method_to_apply_changes_X(self, data):

		'''
			Method for implementing changes to setting x.

		'''

		log('hells yeah!')

	def translate_on_populate_X(self, data, reverse=False):

		'''
			Method to translate the data before adding to the setting_data_method dict.

			This is useful if you are getting the populating from an external source like the Pi's config.txt.
			This method could end with a call to another method to populate the settings.xml from that same source.
		'''

		# this is how you would negate the translateing of the data when the settings window closes.
		if reverse:
			return data

	#																															 #
	##############################################################################################################################

if __name__ == "__main__":
	pass