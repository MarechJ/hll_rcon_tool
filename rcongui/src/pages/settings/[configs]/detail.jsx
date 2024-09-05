import { useLoaderData } from "react-router-dom";
import UserSettings from "../../../components/UserSettings";
import { get } from "../../../utils/fetchUtils";

export const loader = async ({ params }) => {
    const { category, type } = params;
    let note, data, details, configTypes;

    // Dynamically load JSON based on route parameters
    try {
        const configMappingModule = await import("../_data/mappings")

        if (!configMappingModule[category]) throw new Error()

        configTypes = configMappingModule[category];

        note = await import(`../_data/${category}/${type}.js`);
                
        details = configTypes.find(configType => type === configType.path.split('/').slice(-1)[0])
        console.log(details)
        if (!details) throw new Error()
    } catch (error) {
        throw new Response('Webhook not found', { status: 404 });
    }

    try {
        const response = await get(`get_${details.command}`)
        data = await response.json();
        if (!data || data.failed) throw new Error()
    } catch (error) {
        throw new Response('Could not load config data', { status: 400 })
    }

    return {
        note: note.default, // .default is needed because dynamic imports return an ES module object
        data: JSON.stringify(data.result, null, 2),
        ...details,
    }; 
  }

const Webhook = () => {
    const { note, command, name, data } = useLoaderData();

    return (
        <UserSettings
            description={name}
            getEndpoint={`get_${command}`}
            setEndpoint={`set_${command}`}
            validateEndpoint={`validate_${command}`}
            describeEndpoint={`describe_${command}`}
            notes={note}
            data={data}
        />
    )
}

export default Webhook;