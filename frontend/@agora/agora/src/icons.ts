import {
	BadgeCheck,
	BadgeSwissFranc,
	Ban,
	CircleAlert,
	CircleUser,
	createIcons,
	DollarSign,
	Fingerprint,
	Globe,
	HatGlasses,
	IdCard,
	Info,
	LogIn,
	Menu,
	Moon,
	Palette,
	RefreshCw,
	Sun,
	SunMoon,
	Upload,
	UserRoundCheck,
	X,
} from "lucide";

const runIcons = () => {
	createIcons({
		icons: {
			BadgeCheck,
			BadgeSwissFranc,
			Ban,
			CircleAlert,
			CircleUser,
			DollarSign,
			Fingerprint,
			Globe,
			HatGlasses,
			IdCard,
			Info,
			LogIn,
			Menu,
			Moon,
			Palette,
			RefreshCw,
			Sun,
			SunMoon,
			Upload,
			UserRoundCheck,
			X,
		},
	});
};

runIcons();

document.addEventListener("agora:icons:refresh", () => {
	runIcons();
});
